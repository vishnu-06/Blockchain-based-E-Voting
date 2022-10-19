import time, datetime
import uuid
from django.contrib import messages
from Crypto.Signature import DSS
from Crypto.Hash import SHA3_256
from Crypto.PublicKey import ECC
from Crypto import Random
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
import math
import requests
from accounts.models import Activation
from accounts.utils import mail
from simulation.models import Election, Candidate, Vote, Block, VoteBackup
from firebase import firebase
firebase = firebase.FirebaseApplication('https://pdc-project-25f06-default-rtdb.asia-southeast1.firebasedatabase.app/', None)

def create(request):
    if request.method == 'POST' and request.user.is_authenticated:
        voter_id = request.POST.get('voter-id-input')
        vote = request.POST.get('vote-input')
        private_key = request.POST.get('private-key-input')

        votes_total = Vote.objects.all().count() + 1
        block_id = math.ceil(votes_total/settings.N_TX_PER_BLOCK)

        # Create ballot as string vector
        timestamp = datetime.datetime.now().timestamp() * 10**5
        ballot = "{}|{}|{}".format(voter_id, vote, timestamp)
        print('\ncasted ballot: {}\n'.format(ballot))
        signature = ''
        try:
            # Create signature
            priv_key = ECC.import_key(private_key)
            h = SHA3_256.new(ballot.encode('utf-8'))
            signature = DSS.new(priv_key, 'fips-186-3').sign(h)
            print('\nsignature: {}\n'.format(signature.hex()))
            print(private_key)

            # Verify the signature using registered public key
            public_key = Activation.objects.filter(user_id = request.user.id)[0]
            print(public_key.public_key_ecc)
            pub_key = ECC.import_key(public_key.public_key_ecc)
            verifier = DSS.new(pub_key, 'fips-186-3')
        
            print(verifier.verify(h, signature))
            status = 'The ballot is signed successfully.'
            new_vote = Vote(id=voter_id, vote=vote, timestamp=timestamp, block_id=block_id)
            vote_data = {'Id': voter_id,
                    'Vote': vote,
                    'Timestamp': timestamp,
                    'Block_Id': block_id,
                    }
            requests.put('https://pdc-project-25f06-default-rtdb.asia-southeast1.firebasedatabase.app/voter_data.json', vote_data)
            new_backup_vote = VoteBackup(id=voter_id, vote=vote, timestamp=timestamp, block_id=block_id)
            new_vote.save()
            new_backup_vote.save()
            election = Election.objects.filter(is_open = True).first()
            mail("Your vote has been cast successfully", request.user.email, str(election.name) + " - Voting Successful")
            error = False
        except (ValueError, TypeError):
            status = 'The key is not registered.'
            error = True
            messages.info(request, status, extra_tags='bg-info')
        context = {
            'ballot': ballot,
            'signature': signature,
            'status': status,
            'error': error,
        }
        return redirect('index')
    if request.user.is_authenticated:
        election = Election.objects.filter(is_open = True).first()
        candidates = Candidate.objects.filter(election = election.id)
        context = {'voter_id': uuid.uuid4(), 'election': election, 'candidates': candidates}
        return render(request, 'ballot/create.html', context)
    else:
        return redirect('index')

def seal(request):
    print("HERE")
    if request.method == 'POST' and request.user.is_authenticated:
        ballot = request.POST.get('ballot_input')
        ballot_byte = ballot.encode('utf-8')
        ballot_hash = SHA3_256.new(ballot_byte).hexdigest()
        # Puzzle requirement: '0' * n (n leading zeros)
        puzzle, pcount = settings.PUZZLE, settings.PLENGTH
        nonce = 0

        # Try to solve puzzle
        start_time = time.time() # benchmark
        timestamp = datetime.datetime.now().timestamp() # mark the start of mining effort
        while True:
            block_hash = SHA3_256.new(("{}{}{}".format(ballot, nonce, timestamp).encode('utf-8'))).hexdigest()
            print('\ntrial hash: {}\n'.format(block_hash))
            if block_hash[:pcount] == puzzle:
                stop_time = time.time() # benchmark
                print("\nblock is sealed in {} seconds\n".format(stop_time-start_time))
                break
            nonce += 1
        

        context = {
            'prev_hash': 'GENESIS',
            'transaction_hash': ballot_hash,
            'nonce': nonce,
            'block_hash': block_hash,
            'timestamp': timestamp,
        }
        return render(request, 'ballot/seal.html', context)
    if request.user.is_authenticated:
        return redirect('ballot:create')
    else:
        return redirect('index')
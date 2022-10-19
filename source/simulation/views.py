import datetime, time, json, math
import random
import uuid
import os
import requests
from Crypto.Hash import SHA3_256
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.safestring import mark_safe
from simulation.models import Election, Candidate
from app.conf.development.settings import *
from django.db import transaction
from .models import Vote, Block, VoteBackup, Election, Candidate

from firebase import firebase
firebase = firebase.FirebaseApplication('https://pdc-project-25f06-default-rtdb.asia-southeast1.firebasedatabase.app/', None)

def generate(request):
    number_of_tx_per_block = settings.N_TX_PER_BLOCK
    # Generate transactions.
    time_start = time.time()
    block_no = 1
    all_votes = Vote.objects.all()
    for i in range(len(all_votes)):
        # generate random, valid values
        v_id = all_votes[i].id
        v_cand = all_votes[i].vote
        v_timestamp = all_votes[i].timestamp
        # directly fill the values and the block id for simulation purpose
        new_vote = Vote(id=v_id, vote=v_cand, timestamp=v_timestamp, block_id=block_no)
        new_backup_vote = VoteBackup(id=v_id, vote=v_cand, timestamp=v_timestamp, block_id=block_no)
        # "Broadcast" to two nodes
        #new_vote.save()
        #new_backup_vote.save()
        print("#{} new vote: {}".format(i, new_vote)) # for sanity
        if i % number_of_tx_per_block == 0:
            block_no += 1
    time_end = time.time()
    print('\nFinished in {} seconds.\n'.format(time_end - time_start))

    # View the generated transactions
    votes = Vote.objects.order_by('-timestamp')[:100] # only shows the last 100, if any
    election = Election.objects.filter(is_open = False).first()
    candidates = Candidate.objects.filter(election = election.id)
    context = {
        'votes': votes,
        'election': election,
        'candidates': candidates
    }
    request.session['transactions_done'] = True
    return render(request, 'simulation/generate.html', context)

def generate_votes(request):
    #"""Generate transactions and fill them with valid values."""
    number_of_transactions = Vote.objects.all().count()
    number_of_tx_per_block = settings.N_TX_PER_BLOCK

    # Delete all data from previous demo.
    deleted_old_votes = Vote.objects.all().delete()[0]
    VoteBackup.objects.all().delete()
    print('\nDeleted {} data from previous simulation.\n'.format(deleted_old_votes))
    # Delete all blocks from previous demo.
    deleted_old_blocks = Block.objects.all().delete()[0]
    print("\nDeleted {} blocks from previous simulation.\n".format(deleted_old_blocks))
    
    # Generate transactions.
    time_start = time.time()
    block_no = 1
    vote_dict = "{"
    transaction.set_autocommit(False, using=None)
    prev_timestamp = None
    for i in range(1, N_TRANSACTIONS + 1):
        # generate random, valid values
        v_id = uuid.uuid4()
        v_cand = random.randint(1,2)
        v_timestamp = datetime.datetime.now().timestamp() * 10**5
        if v_timestamp == prev_timestamp:
            v_timestamp += 1
        prev_timestamp = v_timestamp
        # directly fill the values and the block id for simulation purpose
        new_vote = Vote(id=v_id, vote=v_cand, timestamp=v_timestamp, block_id=block_no)
        new_backup_vote = VoteBackup(id=v_id, vote=v_cand, timestamp=v_timestamp, block_id=block_no)
        # "Broadcast" to two nodes
        new_vote.save()
        new_backup_vote.save()
        if i == N_TRANSACTIONS:
            vote_data = '"' + str(v_id) + '" : {"Vote" : "' + str(v_cand) + '", "Timestamp" : "' + str(v_timestamp) + '", "Block_Id" : "' + str(block_no) + '"}'
        else:
            vote_data = '"' + str(v_id) + '" : {"Vote" : "' + str(v_cand) + '", "Timestamp" : "' + str(v_timestamp) + '", "Block_Id" : "' + str(block_no) + '"}, '
        vote_dict = vote_dict + vote_data
        print("#{} new vote: {}".format(i, new_vote)) # for sanity
        if i % number_of_tx_per_block == 0:
            block_no += 1
    transaction.commit()
    transaction.set_autocommit(True, using=None)    
    requests.put('https://pdc-project-25f06-default-rtdb.asia-southeast1.firebasedatabase.app/voter_data.json', vote_dict + "}")
    time_end = time.time()
    print('\nFinished in {} seconds.\n'.format(time_end - time_start))
    # View the generated transactions
    votes = Vote.objects.order_by('-timestamp')[:100] # only shows the last 100, if any
    election = Election.objects.filter(is_open = False).first()
    candidates = Candidate.objects.filter(election = election.id)
    context = {'votes': votes, 'election': election, 'candidates': candidates}
    request.session['transactions_done'] = True
    return render(request, 'simulation/generate.html', context)

def seal(request):
    """Seal the transactions generated previously."""
    exec(open("./mining.py").read())
    n = 0
    number_of_blocks = math.ceil(Vote.objects.all().count()/settings.N_TX_PER_BLOCK)
    while(True):
        if n == number_of_blocks:
            break
        time.sleep(2)
        latest_block = Block.objects.filter(id = n + 1)
        if len(latest_block):
            n += 1

    # if request.session.get('transactions_done') is None:
    #     redirect('index')
    # del request.session['transactions_done']

    # Puzzle requirement: '0' * (n leading zeros)
    return redirect('simulation:blockchain')

def transactions(request):
    """See all transactions that have been contained in blocks."""
    vote_list = Vote.objects.all().order_by('timestamp')
    paginator = Paginator(vote_list, 100, orphans=20, allow_empty_first_page=True)

    page = request.GET.get('page')
    votes = paginator.get_page(page)

    hashes = [SHA3_256.new(str(v).encode('utf-8')).hexdigest() for v in votes]
    
    # This happens if you don't use foreign key
    block_hashes = []
    for i in range(0, len(votes)):
        try:
            b = Block.objects.get(id=votes[i].block_id)[0]
            h = b.h
        except:
            h = 404
        block_hashes.append(h)
    
    # zip the three iters
    votes_pg = votes # for pagination
    votes = zip(votes, hashes, block_hashes)

    election = Election.objects.filter(is_open = False)
    if(len(election)):
        election = Election.objects.filter(is_open = False).first()
        candidates = Candidate.objects.filter(election_id = election.id)
    else:
        election = []
        candidates = []
    # Calculate the voting result of 3 cands, the ugly way
    result = []
    for i in range(len(candidates)):
        try:
            r = Vote.objects.filter(vote=i+1).count()
        except:
            r = 0
        result.append(r)

    context = {
        'votes': votes,
        'result': result,
        'candidates': candidates,
        'election': election,
        'votes_pg': votes_pg,

    }
    return render(request, 'simulation/transactions.html', context)

def blockchain(request):
    """See all mined blocks."""
    blocks = Block.objects.all().order_by('id')
    context = {
        'blocks': blocks,
    }
    return render(request, 'simulation/blockchain.html', context)

def verify(request):
    """Verify transactions in all blocks by re-calculating the merkle root."""
    # Basically, by just creating a session (message) var

    print('verifying data...')
    number_of_blocks = Block.objects.all().count()
    corrupt_block_list = ''
    transactions_from_firebase = firebase.get('/voter_data','')
    vote_verification_message = ""
    for i in range(1, number_of_blocks + 1):
        # Select block #i
        b = Block.objects.get(id=i)
        # Select all transactions in block #i
        transactions = Vote.objects.filter(block_id=i).order_by('timestamp')
        for vote in transactions:
            vote_obj = transactions_from_firebase[str(vote.id)]
            if vote_obj['Vote'] != str(vote.vote):
                vote_verification_message = vote_verification_message + "<br/>Vote ID: " + str(vote.id) + " is tampered"
                print("Vote ID: " + str(vote.id) + " is tampered\n")            

        # Verify them
        root = MerkleTools()
        root.add_leaf([str(tx) for tx in transactions], True)
        root.make_tree()
        merkle_h = root.get_merkle_root()
        
        if b.merkle_h == merkle_h:
            message = 'Block {} verified.'.format(i)
        else:
            message = 'Block {} is TAMPERED'.format(i)
            corrupt_block_list += ' {}'.format(i)
        print('{}'.format(message))
    if len(corrupt_block_list) > 0:
        messages.warning(request, mark_safe('The following blocks have corrupted transactions: {}. \n {}'.format(corrupt_block_list, vote_verification_message)), extra_tags='bg-danger')
    else:
        messages.info(request, 'All transactions in blocks are intact.', extra_tags='bg-info')
    return redirect('simulation:blockchain')

def sync(request):
    """Restore transactions from honest node."""
    deleted_old_votes = Vote.objects.all().delete()[0]
    print('\nTrying to sync {} transactions with 1 node(s)...\n'.format(deleted_old_votes))
    bk_votes = VoteBackup.objects.all().order_by('timestamp')
    transaction.set_autocommit(False, using=None)
    for bk_v in bk_votes:
        vote = Vote(id=bk_v.id, vote=bk_v.vote, timestamp=bk_v.timestamp, block_id=bk_v.block_id)
        vote.save()
    transaction.commit()
    transaction.set_autocommit(True, using=None)
    print('\nSync complete.\n')
    messages.info(request, 'All blocks have been synced successfully.')
    return redirect('simulation:blockchain')

def sync_with_firebase(request):
    """Restore transactions from firebase."""
    deleted_old_votes = Vote.objects.all().delete()[0]
    print('\nTrying to sync {} transactions with 1 node(s)...\n'.format(deleted_old_votes))
    transactions_from_firebase = firebase.get('/voter_data','')
    transaction.set_autocommit(False, using=None)
    print(transactions_from_firebase.keys())
    for key in transactions_from_firebase.keys():
        vote_obj = transactions_from_firebase[key]
        vote = Vote(id=key, vote=vote_obj['Vote'], timestamp=vote_obj['Timestamp'], block_id=vote_obj['Block_Id'])
        vote.save()
    transaction.commit()
    transaction.set_autocommit(True, using=None)
    print('\nSync with Firebase complete.\n')
    messages.info(request, 'All blocks have been synced successfully.')
    return redirect('simulation:blockchain')

def sync_block(request, block_id):
    """Restore transactions of a block from honest node."""
    b = Block.objects.get(id=block_id)
    print('\nSyncing transactions in block {}\n'.format(b.id))
    # Get all existing transactions in this block and delete them
    Vote.objects.filter(block_id=block_id).delete()
    # Then rewrite from backup node
    bak_votes = VoteBackup.objects.filter(block_id=block_id).order_by('timestamp')
    for bv in bak_votes:
        v = Vote(id=bv.id, vote=bv.vote, timestamp=bv.timestamp, block_id=bv.block_id)
        v.save()
    # Just in case, delete transactions without valid block
    block_count = Block.objects.all().count()
    Vote.objects.filter(block_id__gt=block_count).delete()
    Vote.objects.filter(block_id__lt=1).delete()
    print('\nSync complete\n')
    return redirect('simulation:block_detail', block_hash=b.h)

def block_detail(request, block_hash):
    """See the details of a block and its transactions."""
    # Select the block or 404
    block = get_object_or_404(Block, h=block_hash)
    confirmed_by = (Block.objects.all().count() - block.id) + 1
    # Select all corresponding transactions
    transaction_list = Vote.objects.filter(block_id=block.id).order_by('timestamp')
    paginator = Paginator(transaction_list, 100, orphans=20)

    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    transactions_hashes = [SHA3_256.new(str(t).encode('utf-8')).hexdigest() for t in transactions]
    
    # Check the integrity of transactions
    root = MerkleTools()
    root.add_leaf([str(tx) for tx in transaction_list], True)
    root.make_tree()
    merkle_h = root.get_merkle_root()
    tampered = block.merkle_h != merkle_h
    
    transactions_pg = transactions # for pagination
    transactions = zip(transactions, transactions_hashes)
    
    # Get prev and next block id
    prev_block = Block.objects.filter(id=block.id - 1).first()
    next_block = Block.objects.filter(id=block.id + 1).first()

    context = {
        'bk': block,
        'confirmed_by': confirmed_by,
        'transactions': transactions,
        'tampered': tampered,
        'verified_merkle_h': merkle_h,
        'prev_block': prev_block,
        'next_block': next_block,
        'transactions_pg': transactions_pg,
    }

    return render(request, 'simulation/block.html', context)

# HELPER FUNCTIONS
def _get_vote():
    return randint(1, 3)

def _get_timestamp():
    return datetime.datetime.now().timestamp()

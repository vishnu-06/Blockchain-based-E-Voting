from multiprocessing import Pool
from multiprocessing.context import Process
from django.conf import settings
from Crypto.Hash import SHA3_256
import datetime, time, math
import django
from django.db import transaction
from app.settings import DATABASES, INSTALLED_APPS
import os
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "app.settings"
)
django.setup()
from simulation.models import Vote, Block
from simulation.merkle.merkle_tool import MerkleTools

def Mine(i, prev_hash, merkle_h, nonce, timestamp):
    puzzle, pcount = settings.PUZZLE, settings.PLENGTH
    start_nonce = nonce
    while True:
        enc = ("{}{}{}{}".format(prev_hash, merkle_h, nonce, timestamp)).encode('utf-8')
        h = SHA3_256.new(enc).hexdigest()
        if h[:pcount] == puzzle:
            block = Block(id=i, prev_h=prev_hash, merkle_h=merkle_h, h=h, nonce=nonce, timestamp=timestamp)
            block.save()
            break
        nonce += 1
        if nonce - start_nonce == 100000:
            nonce += 400000
    return

if __name__ == '__main__':

    """Seal the transactions generated previously."""
    # if request.session.get('transactions_done') is None:
    #     redirect('index')
    # del request.session['transactions_done']

    # Puzzle requirement: '0' * (n leading zeros)
    puzzle, pcount = settings.PUZZLE, settings.PLENGTH

    # Seal transactions into blocks
    deleted_old_blocks = Block.objects.all().delete()
    time_start = time.time()
    number_of_blocks = math.ceil(Vote.objects.all().count()/settings.N_TX_PER_BLOCK)
    transaction.set_autocommit(False, using=None)
    

    for i in range(1, number_of_blocks + 1):
        block_transactions = Vote.objects.filter(block_id=i).order_by('timestamp')
        if(i == 1):
            prev_hash = '0' * 64
        else:
            prev_hash = Block.objects.filter(id = i - 1)[0].h
        root = MerkleTools()
        root.add_leaf([str(tx) for tx in block_transactions], True)
        root.make_tree()
        merkle_h = root.get_merkle_root()
        
        # Try to seal the block and generate valid hash
        nonce = 0
        timestamp = round(datetime.datetime.now().timestamp(), 12)

        p1 = Process(target = Mine, args=(i, prev_hash, merkle_h, nonce, timestamp,))
        p2 = Process(target = Mine, args=(i, prev_hash, merkle_h, nonce + 100000, timestamp,))
        p3 = Process(target = Mine, args=(i, prev_hash, merkle_h, nonce + 200000, timestamp,))
        p4 = Process(target = Mine, args=(i, prev_hash, merkle_h, nonce + 300000, timestamp,))
        p5 = Process(target = Mine, args=(i, prev_hash, merkle_h, nonce + 400000, timestamp,))
        p1.start()
        p2.start()
        p3.start()
        p4.start()
        p5.start()
        while(True):
            b = Block.objects.filter(id = i)
            if(len(b)):
                p1.kill()
                p2.kill()
                p3.kill()
                p4.kill()
                p5.kill()
                break

        # Create the block

        print('\nBlock {} is mined'.format(i))
    transaction.commit()
    transaction.set_autocommit(True, using=None)
    time_end = time.time()
    print('\nSuccessfully created {} blocks.\n'.format(number_of_blocks))
    print('\nFinished in {} seconds.\n'.format(time_end - time_start))
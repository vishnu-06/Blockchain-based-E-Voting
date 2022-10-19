import datetime, uuid, random
from django.db import models
from django.contrib import admin

def get_vote():
    return random.randint(1, 3)

def get_timestamp():
    return datetime.datetime.now().timestamp()

class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vote = models.IntegerField(default=get_vote)
    timestamp = models.FloatField(default=get_timestamp)
    block_id = models.IntegerField(null=True)

    def __str__(self):
        return "{}|{}|{}".format(self.id, self.vote, self.timestamp)

class Block(models.Model):
    prev_h = models.CharField(max_length=64, blank=True)
    merkle_h = models.CharField(max_length=64, blank=True)
    h = models.CharField(max_length=64, blank=True)
    nonce = models.IntegerField(null=True)
    timestamp = models.FloatField(default=get_timestamp)

    def __str__(self):
        return str(self.id)

class VoteBackup(models.Model):
    """This model acts as backup; its objects shall never be tampered."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vote = models.IntegerField(default=get_vote)
    timestamp = models.FloatField(default=get_timestamp)
    block_id = models.IntegerField(null=True)

    def __str__(self):
        return "{}|{}|{}".format(self.id, self.vote, self.timestamp)

class Election(models.Model):
    name = models.CharField(max_length=64)
    is_open = models.BooleanField()
    
    def __str__(self):
        return str(self.name)

class Candidate(models.Model):
    name = models.CharField(max_length=64)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    party = models.CharField(max_length=64)
    symbol = models.CharField(max_length=64)

    def __str__(self):
        return str(self.name)
    
admin.site.register(Election)
admin.site.register(Candidate)

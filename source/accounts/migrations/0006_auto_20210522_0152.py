# Generated by Django 3.1.7 on 2021-05-21 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_activation_private_key_ecc'),
    ]

    operations = [
        migrations.AddField(
            model_name='activation',
            name='aadhaar_id',
            field=models.CharField(default='', max_length=16),
        ),
        migrations.AddField(
            model_name='activation',
            name='voter_id',
            field=models.CharField(default='', max_length=16),
        ),
        migrations.AddField(
            model_name='activation',
            name='voting_allowed',
            field=models.CharField(default='', max_length=3),
        ),
    ]

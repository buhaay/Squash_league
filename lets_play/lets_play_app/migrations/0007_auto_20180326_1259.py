# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-26 12:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lets_play_app', '0006_messages_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='score',
            old_name='is_confirmed',
            new_name='is_confirmed_by_user_main',
        ),
        migrations.AddField(
            model_name='score',
            name='is_confirmed_by_user_partner',
            field=models.BooleanField(default=False),
        ),
    ]
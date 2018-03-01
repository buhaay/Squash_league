# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-01 12:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lets_play_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='skill',
            field=models.IntegerField(choices=[(1, 'amator'), (2, 'okazjonalny grajek'), (3, 'profesjonalista'), (4, 'terminator squasha')], null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lets_play_app.SportCenter', verbose_name='Wybierz lokalizację'),
        ),
    ]
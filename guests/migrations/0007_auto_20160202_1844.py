# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-03 02:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0006_auto_20160202_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resident',
            name='was_reso',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
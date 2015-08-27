# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyncEntry',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('status', models.CharField(max_length=20, blank=True, null=True, choices=[('pending delete', 'pending delete'), ('pending insert', 'pending insert'), ('pending update', 'pending update'), ('success', 'success'), ('fail', 'fail')])),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('attempts', models.IntegerField(default=0)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', blank=True, null=True)),
            ],
        ),
    ]

# Generated by Django 4.2.6 on 2023-10-29 11:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0006_mtmreplyrating'),
    ]

    operations = [
        migrations.AddField(
            model_name='reply',
            name='date_create',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]

# Generated by Django 3.1.4 on 2020-12-23 04:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('auctions', '0014_auto_20201219_1214'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='author_name',
            field=models.TextField(default='rakesh', max_length=150),
            preserve_default=False,
        ),
    ]

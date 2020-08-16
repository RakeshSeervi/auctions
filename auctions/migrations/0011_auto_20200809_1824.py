# Generated by Django 3.0.8 on 2020-08-09 18:24

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_auto_20200808_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='watchers',
            field=models.ManyToManyField(related_name='watchlist', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='bid',
            name='bidValue',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='listing',
            name='basePrice',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(choices=[('other', ''), ('electronics', 'Electronics'), ('furniture', 'Furniture'), ('vehicle', 'Vehicle'), ('fashion', 'Fashion')], default='other', max_length=11),
        ),
    ]

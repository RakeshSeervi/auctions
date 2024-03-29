# Generated by Django 3.0.8 on 2020-08-08 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_auto_20200808_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(choices=[('electronics', 'Electronics'), ('furniture', 'Furniture'), ('vehicle', 'Vehicle'), ('fashion', 'Fashion'), ('other', 'Other')], default='other', max_length=11),
        ),
    ]

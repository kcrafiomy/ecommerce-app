# Generated by Django 4.2.4 on 2023-09-17 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userside', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='address1',
            field=models.TextField(blank=True),
        ),
    ]

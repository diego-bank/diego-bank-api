# Generated by Django 4.2.6 on 2023-10-20 18:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='cnpj',
        ),
    ]

# Generated by Django 4.2.6 on 2023-10-23 16:28

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_user_cnpj'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='url_image',
            field=models.ImageField(null=True, upload_to=core.models.user_image_field),
        ),
    ]

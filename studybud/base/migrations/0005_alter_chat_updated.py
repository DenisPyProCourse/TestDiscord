# Generated by Django 4.1.3 on 2022-12-16 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_chat_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
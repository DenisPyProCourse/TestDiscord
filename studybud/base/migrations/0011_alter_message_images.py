# Generated by Django 4.1.3 on 2022-12-20 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_alter_message_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='images',
            field=models.ImageField(default='avatar.svg', null=True, upload_to='images/'),
        ),
    ]
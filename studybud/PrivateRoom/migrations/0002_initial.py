# Generated by Django 4.1.3 on 2023-01-10 14:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('PrivateRoom', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='private_room',
            name='host',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='private_room',
            name='room_friends',
            field=models.ManyToManyField(blank=True, related_name='room_friends', to=settings.AUTH_USER_MODEL),
        ),
    ]
# Generated by Django 4.1.3 on 2023-01-12 13:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_friend', models.BooleanField(default=False)),
                ('friend', models.ManyToManyField(related_name='friends', to=settings.AUTH_USER_MODEL, verbose_name='Friend')),
                ('host_friend', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='host_friend', to=settings.AUTH_USER_MODEL, verbose_name='Host friend')),
            ],
        ),
    ]
# Generated by Django 3.1.7 on 2021-03-27 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='signature',
            field=models.CharField(default='none', max_length=200),
        ),
    ]

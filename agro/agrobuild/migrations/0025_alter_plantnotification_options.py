# Generated by Django 5.2 on 2025-05-09 08:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agrobuild', '0024_plantnotification_allow_push_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='plantnotification',
            options={'ordering': ['-created_at']},
        ),
    ]

# Generated by Django 5.1.5 on 2025-02-13 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0003_featureditem'),
    ]

    operations = [
        migrations.AddField(
            model_name='craftitem',
            name='featured',
            field=models.BooleanField(default=False),
        ),
    ]

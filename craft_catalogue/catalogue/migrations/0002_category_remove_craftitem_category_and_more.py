# Generated by Django 5.1.5 on 2025-02-13 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='craftitem',
            name='category',
        ),
        migrations.AlterField(
            model_name='artist',
            name='website',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='craftitem',
            name='categories',
            field=models.ManyToManyField(related_name='items', to='catalogue.category'),
        ),
    ]

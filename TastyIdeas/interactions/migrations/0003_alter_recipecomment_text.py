# Generated by Django 4.2.11 on 2024-03-22 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactions', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipecomment',
            name='text',
            field=models.CharField(max_length=500),
        ),
    ]

# Generated by Django 2.0.5 on 2018-05-27 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0018_auto_20180526_2025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, default='', upload_to='C:\\Users\\cbaldwin\\Documents\\teamTreehouseProjects\\Python\\project_12\\p_12\\media'),
        ),
    ]

# Generated by Django 2.0.5 on 2018-05-15 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0008_auto_20180513_0641'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='', upload_to='media'),
        ),
    ]
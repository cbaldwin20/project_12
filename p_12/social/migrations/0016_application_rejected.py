# Generated by Django 2.0.5 on 2018-05-25 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0015_application_applied_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='rejected',
            field=models.BooleanField(default=False),
        ),
    ]
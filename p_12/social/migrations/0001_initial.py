# Generated by Django 2.0.5 on 2018-05-07 09:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('desciption', models.TextField()),
                ('project_time', models.TextField()),
                ('application_requirements', models.TextField()),
                ('owner', models.ForeignKey(on_delete=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField()),
                ('user', models.ManyToManyField(related_name='skills', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='positions',
            field=models.ManyToManyField(related_name='skills', to='social.Skill'),
        ),
        migrations.AddField(
            model_name='profile',
            name='projects',
            field=models.ManyToManyField(to='social.Project'),
        ),
        migrations.AddField(
            model_name='profile',
            name='skill',
            field=models.ManyToManyField(to='social.Skill'),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
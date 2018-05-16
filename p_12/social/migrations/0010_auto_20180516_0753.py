# Generated by Django 2.0.5 on 2018-05-16 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0009_profile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position_name', models.CharField(max_length=255)),
                ('position_description', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='project',
            name='skills',
        ),
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='', upload_to='C:\\Users\\cbaldwin\\Documents\\teamTreehouseProjects\\Python\\project_12\\p_12\\media'),
        ),
        migrations.AddField(
            model_name='position',
            name='project',
            field=models.ForeignKey(on_delete=True, related_name='project_positions', to='social.Project'),
        ),
    ]

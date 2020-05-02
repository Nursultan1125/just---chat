# Generated by Django 3.0.5 on 2020-04-29 15:58
from django.apps import apps
from django.db import migrations, models


def create_default_user_categories(apps, schema_editor):
    ConnectionPerson = apps.get_model('chat', 'ConnectionPerson')
    ConnectionPerson.objects.create(id=1, count_connection=0).save()

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConnectionPerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count_connection', models.IntegerField(default=0)),
            ],
        ),
        migrations.RunPython(create_default_user_categories)
    ]

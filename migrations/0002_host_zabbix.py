# Generated by Django 3.1.7 on 2023-05-24 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zabbix_omoc', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Host_zabbix',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(max_length=100, null=True)),
                ('host_name', models.CharField(max_length=200, null=True)),
            ],
        ),
    ]
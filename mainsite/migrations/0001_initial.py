# Generated by Django 4.2.2 on 2023-07-20 07:56

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('name', models.CharField(default='Unknown', editable=False, max_length=20)),
                ('vatNumber', models.CharField(default='00000000', max_length=8, primary_key=True, serialize=False, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField(default=0.0)),
                ('description', models.TextField(blank=True)),
                ('carbonEmission', models.FloatField(default=0.0, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CName', models.CharField(default='未知', max_length=50)),
                ('EName', models.CharField(default='Unknown', max_length=50)),
                ('carbonEmission', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='Transportation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
                ('carbonEmission', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
                ('password', models.CharField(default='', max_length=200)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('phone', models.CharField(max_length=50, unique=True)),
                ('wallet', models.PositiveBigIntegerField(default=0, editable=False)),
                ('last_login', models.DateTimeField(auto_now=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startPlace', django.contrib.gis.db.models.fields.PointField(blank=True, default=(0.0, 0.0), srid=4326)),
                ('endPlace', django.contrib.gis.db.models.fields.PointField(blank=True, default=(0.0, 0.0), srid=4326)),
                ('routeLength', models.FloatField(blank=True, default=0.0)),
                ('carbonEmission', models.FloatField(default=0.0, editable=False)),
                ('dateTime', models.DateTimeField(auto_now_add=True, null=True)),
                ('start', models.CharField(editable=False, max_length=200, null=True)),
                ('end', models.CharField(editable=False, max_length=200, null=True)),
                ('transportation', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='mainsite.transportation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainsite.user')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('description', models.TextField(blank=True)),
                ('photo', models.ImageField(blank=True, upload_to='product_photo')),
                ('carbonEmission', models.FloatField(default=0.0, editable=False)),
                ('company', models.ForeignKey(default='11111111', on_delete=django.db.models.deletion.CASCADE, related_name='products', to='mainsite.company')),
                ('materials', models.ManyToManyField(related_name='products', through='mainsite.Component', to='mainsite.material')),
            ],
        ),
        migrations.AddField(
            model_name='component',
            name='material',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='mainsite.material'),
        ),
        migrations.AddField(
            model_name='component',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='mainsite.product'),
        ),
    ]
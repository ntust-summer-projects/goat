# Generated by Django 4.2.2 on 2023-07-22 01:54

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone', models.CharField(blank=True, max_length=50, null=True)),
                ('role', models.CharField(choices=[('ADMIN', 'Admin'), ('NORMAL', 'Normal'), ('COMPANY', 'Company')], default='ADMIN', max_length=50)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AbstractLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logType', models.CharField(choices=[('TRANSPORTATION', 'transportation'), ('ITEM', 'item')], default='TRANSPORTATION', max_length=50)),
                ('carbonEmission', models.FloatField(default=0.0, editable=False)),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
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
            options={
                'unique_together': {('CName', 'EName')},
            },
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
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('description', models.TextField(blank=True)),
                ('photo', models.ImageField(blank=True, upload_to='product_photo')),
                ('carbonEmission', models.FloatField(default=0.0, editable=False)),
                ('materials', models.ManyToManyField(related_name='products', through='mainsite.Component', to='mainsite.material')),
            ],
        ),
        migrations.CreateModel(
            name='NormalProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('wallet', models.PositiveBigIntegerField(default=0, editable=False)),
                ('carbonProduce', models.DecimalField(decimal_places=4, default=0.0, max_digits=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
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
        migrations.CreateModel(
            name='CompanyProfile',
            fields=[
                ('companyName', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('vatNumber', models.CharField(default='00000000', max_length=8, primary_key=True, serialize=False, unique=True)),
                ('chairman', models.CharField(blank=True, max_length=50, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('mainsite.user',),
            managers=[
                ('company', django.db.models.manager.Manager()),
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='LogI',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('mainsite.abstractlog',),
        ),
        migrations.CreateModel(
            name='LogT',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('mainsite.abstractlog',),
        ),
        migrations.CreateModel(
            name='Normal',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('mainsite.user',),
            managers=[
                ('normal', django.db.models.manager.Manager()),
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='company',
            field=models.ForeignKey(default='11111111', on_delete=django.db.models.deletion.CASCADE, related_name='products', to='mainsite.company'),
        ),
        migrations.CreateModel(
            name='LogTProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.FloatField(blank=True, default=0.0)),
                ('transportation', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='mainsite.transportation')),
                ('log', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mainsite.logt')),
            ],
        ),
        migrations.CreateModel(
            name='LogIProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveBigIntegerField(default=0)),
                ('product', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='mainsite.product')),
                ('log', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mainsite.logi')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='component',
            unique_together={('product', 'material')},
        ),
        migrations.AddField(
            model_name='abstractlog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainsite.normal'),
        ),
    ]

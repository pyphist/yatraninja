# Generated by Django 2.1.7 on 2019-03-27 12:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
        ('companion', '0004_auto_20190327_1521'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=0)),
                ('headline', models.CharField(max_length=250)),
                ('review', models.TextField()),
                ('review_date', models.DateTimeField(auto_now_add=True)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companion.Request')),
                ('traveller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Traveller')),
            ],
        ),
    ]

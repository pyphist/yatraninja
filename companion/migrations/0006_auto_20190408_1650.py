# Generated by Django 2.1.7 on 2019-04-08 11:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('companion', '0005_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='companion',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='companion',
            name='status',
            field=models.CharField(choices=[('INTERESTED', 'INTERESTED'), ('ACCEPTED', 'ACCEPTED'), ('REJECTED', 'REJECTED')], default='INTERESTED', max_length=10),
        ),
    ]

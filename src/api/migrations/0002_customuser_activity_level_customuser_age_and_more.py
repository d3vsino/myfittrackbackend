# Generated by Django 5.2.1 on 2025-05-18 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='activity_level',
            field=models.CharField(blank=True, choices=[('sedentary', 'Sedentary'), ('light', 'Lightly active'), ('moderate', 'Moderately active'), ('active', 'Very active'), ('super', 'Super active')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='age',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='height_cm',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='weight_kg',
            field=models.FloatField(blank=True, null=True),
        ),
    ]

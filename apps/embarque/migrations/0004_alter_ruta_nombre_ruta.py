# Generated by Django 5.2.1 on 2025-06-12 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('embarque', '0003_alter_puerto_nombre_puerto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ruta',
            name='nombre_ruta',
            field=models.CharField(max_length=50),
        ),
    ]

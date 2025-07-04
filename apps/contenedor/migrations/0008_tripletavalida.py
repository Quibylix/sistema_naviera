# Generated by Django 5.2.1 on 2025-06-23 06:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenedor', '0007_alter_bulto_peso_bulto_alter_mercancia_bulto'),
    ]

    operations = [
        migrations.CreateModel(
            name='TripletaValida',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_carga', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenedor.tipocarga')),
                ('tipo_contenedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenedor.tipocontenedor')),
                ('tipo_equipamiento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenedor.tipoequipamiento')),
            ],
            options={
                'verbose_name': 'Combinación válida',
                'verbose_name_plural': 'Combinaciones válidas',
                'unique_together': {('tipo_contenedor', 'tipo_carga', 'tipo_equipamiento')},
            },
        ),
    ]

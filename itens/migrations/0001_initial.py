# Generated by Django 4.1.7 on 2023-02-15 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Itens',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=50)),
                ('barras', models.CharField(max_length=15)),
                ('ativo', models.BooleanField()),
            ],
        ),
    ]
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CloudResourceReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=100)),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
                ('services', models.JSONField()),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('consolidated_at', models.DateTimeField(auto_now_add=True)),
                ('report_hash', models.CharField(blank=True, max_length=64)),
                ('is_valid', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-year', '-month'],
                'unique_together': {('project_name', 'month', 'year')},
            },
        ),
    ]

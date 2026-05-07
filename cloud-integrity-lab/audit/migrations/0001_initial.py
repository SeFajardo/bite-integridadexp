from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detected_at', models.DateTimeField(auto_now_add=True)),
                ('severity', models.CharField(choices=[('INFO', 'Info'), ('WARNING', 'Warning'), ('CRITICAL', 'Critical')], default='CRITICAL', max_length=10)),
                ('message', models.TextField()),
                ('stored_hash', models.CharField(max_length=64)),
                ('computed_hash', models.CharField(max_length=64)),
                ('resolved', models.BooleanField(default=False)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.cloudresourcereport')),
            ],
            options={
                'ordering': ['-detected_at'],
            },
        ),
    ]

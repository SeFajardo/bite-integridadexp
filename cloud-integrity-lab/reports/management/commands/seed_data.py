from decimal import Decimal

from django.core.management.base import BaseCommand

from reports.integrity import compute_report_hash
from reports.models import CloudResourceReport


PROJECTS = ["ProyectoAlpha", "ProyectoBeta", "ProyectoGamma"]
BASE_SERVICES = {"EC2": 150.00, "S3": 30.00, "RDS": 200.00, "Lambda": 15.50}


class Command(BaseCommand):
    help = "Seed the DB with sample cloud cost reports (Jan-Jun 2025)."

    def handle(self, *args, **options):
        created = 0
        for p_idx, project in enumerate(PROJECTS):
            for month in range(1, 7):
                # Slight variation per month/project so values look realistic.
                factor = Decimal('1') + Decimal(p_idx * 0.05) + Decimal(month * 0.02)
                services = {
                    name: float((Decimal(str(cost)) * factor).quantize(Decimal('0.01')))
                    for name, cost in BASE_SERVICES.items()
                }
                total = sum(Decimal(str(v)) for v in services.values())

                report, was_created = CloudResourceReport.objects.update_or_create(
                    project_name=project,
                    month=month,
                    year=2025,
                    defaults={
                        'services': services,
                        'total_cost': total,
                        'currency': 'USD',
                        'is_valid': True,
                    },
                )
                report.report_hash = compute_report_hash(report)
                report.is_valid = True
                report.save(update_fields=['report_hash', 'is_valid'])
                if was_created:
                    created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Datos de prueba creados: {created} reportes para {len(PROJECTS)} proyectos."
        ))

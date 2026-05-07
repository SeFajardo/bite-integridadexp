# Cloud Integrity Lab — Experimento de Integridad de Datos con Hashing

Laboratorio Django + PostgreSQL desplegable en AWS para validar la tactica
arquitectonica de **Hashing** como mecanismo de integridad de datos.

---

## ASR

> Como administrador cloud, cuando se intente realizar una modificacion no
> autorizada en los registros de costos ya consolidados, dado que la veracidad
> de los datos es la base para la facturacion y cumplimiento legal, quiero que
> la informacion de un reporte mensual de un proyecto sea consistente en cada
> consulta del mismo, de forma que el **100% de los intentos de alteracion
> manual en la base de datos sean detectados**, los registros marcados como
> "no integros" sean **bloqueados para el usuario final** y se genere una
> **alerta de seguridad inmediata** en el modulo de auditoria.

---

## Arquitectura

```
                +-------------------------------+
   Cliente ---> |  EC2  cloud-integrity-app     |
   (curl/JMeter)|  Django + DRF  :8080          |
                |  reports/ + audit/            |
                +---------------+---------------+
                                | psycopg2  (5432)
                                v
                +-------------------------------+
                |  EC2  cloud-integrity-db      |
                |  PostgreSQL 16                |
                |  cloud_integrity_db           |
                +-------------------------------+

  Tactica: SHA-256(report) almacenado en columna report_hash.
  En cada GET la app recalcula el hash y lo compara.
  Mismatch -> is_valid=False, AuditAlert CRITICAL, HTTP 403.
```

---

## Endpoints

| Metodo | URL | Descripcion |
|--------|-----|-------------|
| POST | `/api/reports/` | Crear reporte (auto-calcula hash) |
| GET | `/api/reports/` | Listar reportes validos (verifica todos) |
| GET | `/api/reports/<id>/` | Detalle (verifica integridad antes) |
| GET | `/api/reports/<id>/verify/` | Verificacion explicita |
| GET | `/api/reports/stats/` | Totales y conteos |
| GET | `/api/audit/alerts/` | Listar alertas |
| GET | `/api/audit/alerts/<id>/` | Detalle de alerta |
| PATCH | `/api/audit/alerts/<id>/resolve/` | Marcar resuelta |
| GET | `/api/audit/dashboard/` | Resumen de auditoria |

---

## Instalacion local

```bash
git clone <repo>
cd cloud-integrity-lab
pip install -r requirements.txt
cp .env.example .env  # editar con DB_PASSWORD real
createdb cloud_integrity_db
python manage.py migrate
python manage.py seed_data
python manage.py runserver 0.0.0.0:8080
```

---

## Despliegue en AWS

```bash
cd terraform/
terraform init
terraform apply -var="db_password=ChangeMe123!" -var="key_name=mi-keypair"
```

Outputs:
- `app_public_ip` -> IP publica del Django
- `db_private_ip` -> IP privada del Postgres (solo accesible via sg-app)

---

## Ejecutar el experimento completo

```bash
# 1. CREAR
curl -X POST $URL/api/reports/ -H "Content-Type: application/json" \
  -d '{"project_name":"X","month":1,"year":2025,"services":{"EC2":10}}'

# 2. CONSULTAR (200 OK)
curl $URL/api/reports/1/

# 3. ATACAR (modificar DB directamente)
./scripts/simulate_tamper.sh 1 <DB_HOST> postgres cloud_integrity_db

# 4. DETECTAR (403 + AuditAlert CRITICAL creada)
curl -i $URL/api/reports/1/

# 5. AUDITAR
curl $URL/api/audit/alerts/
curl $URL/api/audit/dashboard/
```

Para la guia detallada: ver [`testing/test_guide.md`](testing/test_guide.md).
Para pruebas automatizadas: [`testing/jmeter_plan.jmx`](testing/jmeter_plan.jmx).

---

## Estructura del repositorio

```
cloud-integrity-lab/
├── manage.py
├── requirements.txt
├── .env.example
├── monitoring/         # proyecto Django
├── reports/            # app: reportes + integrity.py
├── audit/              # app: alertas
├── seed/               # wrapper del management command
├── scripts/            # start_app.sh, simulate_tamper.sh
├── terraform/          # infra AWS (VPC default, 2 EC2, 2 SG)
└── testing/            # jmeter_plan.jmx + test_guide.md
```

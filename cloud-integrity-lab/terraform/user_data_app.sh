#!/bin/bash
# user_data_app.sh - Bootstrap del nodo Django (Cloud Integrity Lab)
set -e
exec > /var/log/user_data_app.log 2>&1

apt-get update -y
apt-get install -y python3 python3-pip git

cd /opt
git clone ${repo_url} cloud-integrity-lab || true
cd cloud-integrity-lab/cloud-integrity-lab

pip3 install -r requirements.txt --break-system-packages

cat > .env <<ENV
SECRET_KEY=lab-secret-$(openssl rand -hex 16)
DEBUG=True
DB_NAME=cloud_integrity_db
DB_USER=postgres
DB_PASSWORD=${db_password}
DB_HOST=${db_host}
DB_PORT=5432
ENV

# Wait for the DB to come up before migrating.
for i in $(seq 1 30); do
  if pg_isready -h ${db_host} -p 5432 -U postgres >/dev/null 2>&1; then
    break
  fi
  sleep 5
done

python3 manage.py migrate --noinput
python3 manage.py seed_data || true

nohup python3 manage.py runserver 0.0.0.0:8080 > /var/log/django.log 2>&1 &

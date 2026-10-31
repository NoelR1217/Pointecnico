#!/bin/sh
set -e

echo "==> [PoinTécnico] Verificando migraciones de base de datos..."
python manage.py makemigrations accounts
python manage.py makemigrations tickets

echo "==> [PoinTécnico] Aplicando migraciones a SQLite..."
python manage.py migrate --noinput

echo "==> [PoinTécnico] Cargando datos iniciales y usuarios demostrativos RBAC..."
python manage.py seed_data || true

echo "==> [PoinTécnico] Servidor Django listo. Escuchando en http://0.0.0.0:8000"
exec python manage.py runserver 0.0.0.0:8000

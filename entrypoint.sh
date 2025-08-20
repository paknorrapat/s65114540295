#!/usr/bin/env bash
set -e

# รอ DB ให้พร้อม (ปรับ host/port ตาม compose)
echo "Waiting for database at db:5432..."
until nc -z db 5432; do
  sleep 1
done

echo "Apply migrations"
python manage.py migrate --noinput

# ถ้ามีสคริปต์สร้าง user เริ่มต้น
if [ -f "create_user.py" ]; then
  echo "Ensure default user"
  python create_user.py || true
fi

echo "Collect static "
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"

# ระบบจัดการคลินิกทันตกรรมสปาร์คกี้ 

65114540295 นรภัทร พันรอบ
วิชา Selected Topics in Software Innovation

# วิธีรันโปรเจ็ค
## ต้องมี Docker (สำคัญ)
# 1. โคลนโปรเจ็ค
git clone https://github.com/paknorrapat/65114540295-select-topic.git
# 2. Cd
cd 65114540295-select-topic
# 3. สร้าง Environment
python -m venv venv
# 4. ใช้ Environment
venv\scripts\activate
# 5. ติดตั้งไลบราลี จาก requirements.txt
pip install -r requirements.txt
# 6. สร้าง Database
mysql -u root -p

CREATE DATABASE sparky;

# 7. Migrate
python manage.py migrate

# 8. Runserver
python manage.py runserver


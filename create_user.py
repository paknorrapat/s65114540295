import os
import django

# ตั้งค่า Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from Sparky.models import User,Profile

# ตรวจสอบก่อนว่ามี user อยู่แล้วหรือไม่
if not User.objects.filter(username="doremon99").exists():
    # สร้าง user
    user = User.objects.create_user(
        username="doremon99",
        email="Doremon@gmail.com",
        password="1234",
        is_staff=False,
        is_dentist=False,
        is_manager=False,
        title="นาย",
        first_name="โดเรม่อน",
        last_name="อังอัง",
        
    )
    print("✅ User doremon99 ถูกสร้างแล้ว")
else:
    print("⚠️ User doremon99 มีอยู่แล้ว")
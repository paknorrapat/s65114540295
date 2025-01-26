from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from .models import *
from datetime import time
from django.db.models import UniqueConstraint
# Create your models here.

GENDER_CHOICE = (
    ('ชาย','ชาย'),
    ('หญิง','หญิง'),   
    )
BLOOD_TYPE_CHOICES =(
    ('A','A'),
    ('B','B'),
    ('AB','AB'),
    ('O','O'),
)
class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False,verbose_name='ผนักงานหน้าเคาน์เตอร์')
    is_dentist = models.BooleanField(default=False,verbose_name='ทันตแพทย์')
    is_manager = models.BooleanField(default=False,verbose_name='ผู้จัดการ')
    title = models.CharField(max_length=30,verbose_name="คำนำหน้าชื่อ")

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile')
    idCard = models.CharField(max_length=13,verbose_name='เลขประจำตัวประชาชน')
    phone = models.CharField(max_length=10,verbose_name='เบอร์โทรศัพท์มือถือ')
    address = models.TextField(max_length=500,verbose_name='ที่อยู่')
    birthDate = models.DateField(verbose_name='วันเกิด')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICE, default="ชาย", verbose_name='เพศ')
    weight = models.FloatField(blank=True,null=True,verbose_name='น้ำหนัก')
    height = models.IntegerField(blank=True,null=True,verbose_name='ส่วนสูง')
    bloodType = models.CharField(max_length=10,choices=BLOOD_TYPE_CHOICES,verbose_name='หมู่เลือด')
    ud = models.CharField(max_length=500,blank=True,null=True,verbose_name='โรคประจำตัว')
    image = models.ImageField(upload_to='Image',blank=True,null=True,verbose_name='รูปภาพ')
    allergic = models.CharField(max_length=500,blank=True,null=True,verbose_name='ข้อมูลการแพ้ยา')

    def clean(self):
        if len(self.idCard) != 13:
            raise ValidationError('เลขประจำตัวประชาชนต้องมีความยาว 13 หลัก')
        if self.phone and len(self.phone) != 10:
            raise ValidationError('เบอร์โทรศัพท์มือถือต้องมีความยาว 10 หลัก')
        
    def __str__(self) :
        return self.user.first_name +" "+self.user.last_name

class Treatment(models.Model):
    treatmentName = models.CharField(max_length=100, unique=True,verbose_name="ประเภทการรักษา")
    price = models.FloatField(null=True, blank=True)
    is_braces = models.BooleanField(default=False, verbose_name="เป็นการจัดฟันหรือไม่") 
    createdAt = models.DateTimeField(auto_now_add=True, blank=False)
    updatedAt = models.DateTimeField(auto_now=True, blank=False)

    def __str__(self):
        return self.treatmentName
    
class Dentist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    workDays = models.CharField(max_length=50, verbose_name="วันทำงาน", default="1,2,3,4,5")  # วันทำงาน (1=จันทร์, ..., 7=อาทิตย์)
    startTime = models.TimeField(verbose_name="เวลาเริ่มทำงาน",default=time(9,0))
    endTime = models.TimeField(verbose_name="เวลาหยุดทำงาน",default=time(18,0))
    createdAt = models.DateTimeField(auto_now_add=True, blank=False)
    updatedAt = models.DateTimeField(auto_now=True, blank=False)

    def __str__(self):
        return self.user.first_name


STATUS_CHOICES = [
        ('รอดำเนินการ', 'รอดำเนินการ'),     # Pending
        ('สำเร็จ', 'สำเร็จ'),         # Completed
        ('ไม่สำเร็จ', 'ไม่สำเร็จ'),         # Failed
    ]
class Appointment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    treatment = models.ForeignKey(Treatment,on_delete=models.SET_NULL,null=True,blank=True)
    dentist = models.ForeignKey(Dentist,on_delete=models.SET_NULL,null=True,blank=True)
    date = models.DateField(null=True, blank=True)
    time_slot = models.TimeField(null=True, blank=True)
    status = models.CharField(default='รอดำเนินการ',choices=STATUS_CHOICES, null=True, blank=False,max_length=50)
    detail = models.CharField(max_length=100, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, blank=False)
    updatedAt = models.DateTimeField(auto_now=True, blank=False)

    def __str__(self):
        user_name = self.user.username if self.user else 'Unknown User'
        treatment_name = self.treatment.treatmentName if self.treatment else 'No Treatment'
        return f'{self.user.first_name if self.user else "Unknown"} {self.user.last_name if self.user else ""} : {treatment_name} on {self.date} at {self.time_slot}'

class Extra(models.Model):
    extraName = models.CharField(max_length=100, unique=True,verbose_name="ค่าใช้จ่ายเพิ่มเติม")
    price = models.FloatField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, blank=False)
    updatedAt = models.DateTimeField(auto_now=True, blank=False)
    
    def __str__(self):
        return self.extraName

class TreatmentHistory(models.Model):
    appointment = models.OneToOneField(Appointment,on_delete=models.CASCADE,null=True,blank=True)
    extra = models.ManyToManyField(Extra,blank=True,verbose_name="ค่าใช้จ่ายเพิ่มเติม")
    description = models.TextField(verbose_name='รายละเอียดการรักษา')
    cost = models.FloatField(null=True, blank=True,verbose_name='ค่าใช้จ่าย')
    status = models.BooleanField(default=True,null=True, blank=False)

    def __str__(self):
        # ตรวจสอบว่า appointment และ user มีค่าหรือไม่
        if self.appointment and self.appointment.user:
            user_name = f'{self.appointment.user.title}{self.appointment.user.first_name} {self.appointment.user.last_name}'
        else:
            user_name = 'Unknown User'

        # ตรวจสอบว่า treatment มีค่าหรือไม่
        treatment_name = self.appointment.treatment.treatmentName if self.appointment and self.appointment.treatment else 'No Treatment'

        return f'{user_name} : {treatment_name}'

class ClosedDay(models.Model):
    dentist = models.ForeignKey(Dentist,on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        constraints = [
            UniqueConstraint(fields=['dentist', 'date'], name='unique_dentist_date')
        ]

    def __str__(self):
         return f"{self.dentist.user.first_name} - {self.date}"

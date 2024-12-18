from django.db import models
from datetime import time
# Create your models here.

class Treatment(models.Model):
    treatmentName = models.CharField(max_length=100, unique=True,verbose_name="ประเภทการรักษา")
    createdAt = models.DateTimeField(auto_now_add=True, blank=False)
    updatedAt = models.DateTimeField(auto_now=True, blank=False)

    def __str__(self):
        return self.treatmentName
    
class Dentist(models.Model):
    dentistName = models.CharField(max_length=100, unique=True,verbose_name="ชื่อทันตแพทย์",)
    d_email = models.EmailField(unique=True,verbose_name='อีเมล')
    d_phone = models.CharField(max_length=10, blank=True,verbose_name='เบอร์โทรศัพท์มือถือ')
    workDays = models.CharField(max_length=50, verbose_name="วันทำงาน", default="1,2,3,4,5")  # วันทำงาน (1=จันทร์, ..., 7=อาทิตย์)
    startTime = models.TimeField(verbose_name="เวลาเริ่มทำงาน",default=time(9,0))
    endTime = models.TimeField(verbose_name="เวลาหยุดทำงาน",default=time(18,0))
    createdAt = models.DateTimeField(auto_now_add=True, blank=False)
    updatedAt = models.DateTimeField(auto_now=True, blank=False)

    def __str__(self):
        return self.dentistName
    

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
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





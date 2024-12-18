from django.db import models
from Sparky.models import User
from Category.models import Treatment,Dentist

# Create your models here.
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
        return f'Appointment for {user_name} on {self.date} at {self.time_slot}'

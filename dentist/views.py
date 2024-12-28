from django.shortcuts import render,redirect
from Sparky.models import *
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import *
# Create your views here.
def dentist_home(request):
    # ฟิลเตอร์นัดหมายที่มีวันที่ตรงกับวันนี้ 
    today = timezone.now().date()
    appointment_today = Appointment.objects.filter(date=today,dentist=request.user.dentist).order_by('time_slot')

    # pagination
    paginator = Paginator(appointment_today,5) # แบ่งเป็นหน้า 5 รายการต่อหน้า
    appointment_page_number = request.GET.get('appointment_page')
    appointment_page_obj = paginator.get_page(appointment_page_number)
    return render(request,"dentist/dentist_home.html",{'appointment_page_obj': appointment_page_obj,})

def treatment_history(request):
     # ฟิลเตอร์นัดหมายที่มีวันที่ตรงกับวันนี้ 
    today = timezone.now().date()
    appointment_today = Appointment.objects.filter(date=today,dentist=request.user.dentist,status='สำเร็จ').order_by('time_slot')
    appointments = Appointment.objects.filter(dentist=request.user.dentist).order_by('time_slot')

    # pagination
    paginator = Paginator(appointment_today,5) # แบ่งเป็นหน้า 5 รายการต่อหน้า
    appointment_page_number = request.GET.get('appointment_page')
    appointment_page_obj = paginator.get_page(appointment_page_number)

    # pagination
    paginator = Paginator(appointments,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"dentist/treatment_history.html",{'appointment_page_obj': appointment_page_obj,
                                                            'page_obj':page_obj})

def add_treatment_history(request):
    if request.method == "POST":
        user_id = request.POST.get('user')  # ดึงค่า user จากฟอร์ม
        form = TreatementHistoryForm(request.POST)
        if form.is_valid():
            treatmenthistory = form.save(commit=False)
            treatmenthistory.user_id = user_id
            treatment_history.status = True  # ตั้งค่า status เป็น True
            treatmenthistory.save()
            return redirect("treatment-history")
    return redirect('treatment-history')
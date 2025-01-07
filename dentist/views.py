from django.shortcuts import render,redirect,get_object_or_404
from Sparky.models import *
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import *
from django.db.models import Q
# Create your views here.
def dentist_home(request):
    # ฟิลเตอร์นัดหมายที่มีวันที่ตรงกับวันนี้ 
    today = timezone.now().date()
    appointment_today = Appointment.objects.filter(date=today,dentist=request.user.dentist).order_by('time_slot')
    appointments = Appointment.objects.filter(dentist=request.user.dentist)

    count_appointment_all =appointments.count()
    count_appointment_today =appointment_today.count()
    success_or_fail_today =appointment_today.filter(Q(status="สำเร็จ") | Q(status="ไม่สำเร็จ")).count()
    # pagination
    paginator = Paginator(appointment_today,5) # แบ่งเป็นหน้า 5 รายการต่อหน้า
    appointment_page_number = request.GET.get('appointment_page')
    appointment_page_obj = paginator.get_page(appointment_page_number)

    # pagination
    paginator = Paginator(appointments,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"dentist/dentist_home.html",{'appointment_page_obj': appointment_page_obj,'page_obj':page_obj,'count_appointment_today': count_appointment_today,"success_or_fail_today":success_or_fail_today,"count_appointment_all":count_appointment_all})

def treatment_history(request):
     # ฟิลเตอร์นัดหมายที่มีวันที่ตรงกับวันนี้ 
    today = timezone.now().date()
    appointment_today = Appointment.objects.filter(date=today,dentist=request.user.dentist,status='สำเร็จ').order_by('time_slot')
    appointments = Appointment.objects.filter(dentist=request.user.dentist,status='สำเร็จ',treatmenthistory__status=True)

    count_th_all =appointments.count()
    count_th_today =appointment_today.count()
    success_today =appointment_today.filter(treatmenthistory__status=True).count()

    # pagination
    paginator = Paginator(appointment_today,5) # แบ่งเป็นหน้า 5 รายการต่อหน้า
    appointment_page_number = request.GET.get('appointment_page')
    appointment_page_obj = paginator.get_page(appointment_page_number)

    # pagination
    paginator = Paginator(appointments,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"dentist/treatment_history.html",{'appointment_page_obj': appointment_page_obj,
                                                            'page_obj':page_obj,
                                                            'count_th_all':count_th_all,
                                                            'count_th_today':count_th_today,
                                                            'success_today':success_today,
                                                            })

def t_history_all(request):
    treatment_history = TreatmentHistory.objects.filter(appointment__dentist=request.user.dentist,appointment__status='สำเร็จ', status=True)
    # pagination
    paginator = Paginator(treatment_history,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"dentist/t_history_all.html",{'page_obj':page_obj})

def add_treatment_history(request):
    if request.method == "POST":
        user_id = request.POST.get('user')  # ดึงค่า user จากฟอร์ม
        form = TreatmentHistoryForm(request.POST)
        if form.is_valid():
            treatmenthistory = form.save(commit=False)
            treatmenthistory.user_id = user_id
            treatment_history.status = True  # ตั้งค่า status เป็น True
            treatmenthistory.save()
            return redirect("treatment-history")
    return redirect('treatment-history')

def update_treatment_history(request,treatment_history_id):
    # ดึง TreatmentHistory ที่ต้องการอัปเดต
    treatment_history = get_object_or_404(TreatmentHistory, id=treatment_history_id)
    if request.method == "POST":
        form = TreatmentHistoryForm(request.POST,instance=treatment_history)
        if form.is_valid():
            treatmenthistory = form.save(commit=False)
            treatment_history.status = True  # ตั้งค่า status เป็น True
            treatmenthistory.save()
            return redirect("t-history-all")
    else:
        # GET request: สร้างฟอร์มพร้อมข้อมูลเดิม
        form = TreatmentHistoryForm(instance=treatment_history)
    return render(request,"dentist/update_t_history.html",{'treatment_history':treatment_history})
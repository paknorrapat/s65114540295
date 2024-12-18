from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import *
from .models import *




# Create your views here.
def staff_home(request):
    dentists = Dentist.objects.all() 
    treatments = Treatment.objects.all()
    users = User.objects.all()
    
    appointments = Appointment.objects.all()
    appointment_count = Appointment.objects.count()

    # ฟิลเตอร์นัดหมายที่มีวันที่ตรงกับวันนี้ 
    today = timezone.now().date()
    appointment_today = Appointment.objects.filter(date=today)

    # นับจำนวนของนัดหมายในวันนี้
    appointment_count_today = appointment_today.count()

    # pagination
    paginator = Paginator(appointment_today,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    
    return render(request,"staff/staff_home.html",{
        'appointment_count':appointment_count,
        "appointment_today":appointment_today,
        'appointment_count_today' : appointment_count_today,
        'appointments' : appointments,
        'page_obj': page_obj,
        'dentists':dentists,
        'treatments':treatments,
        'users':users,
        })
def appointment_list(request):
    dentists = Dentist.objects.all() 
    treatments = Treatment.objects.all()
    appointments = Appointment.objects.all()

    appointment_count = Appointment.objects.count()
     # ฟิลเตอร์นัดหมายที่มีวันที่ตรงกับวันนี้ 
    today = timezone.now().date()
    appointment_today = Appointment.objects.filter(date=today)

    # นับจำนวนของนัดหมายในวันนี้
    appointment_count_today = appointment_today.count()

    # pagination
    paginator = Paginator(appointments,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,"staff/appointment_list.html",{
                                                         "appointments":appointments,
                                                         "page_obj":page_obj,
                                                         'appointment_count':appointment_count,
                                                         'appointment_count_today' : appointment_count_today,
                                                         'dentists':dentists,
                                                         'treatments':treatments})

def delete_appointment(request,id):
    appointment = get_object_or_404(Appointment,id=id)
    if request.method == 'POST':
        appointment.delete()
        return redirect('staff-home')
    return redirect('staff-home')

def add_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff-home')
    return redirect('staff-home')


def edit_appointment(request,appointment_id):
    appointment = get_object_or_404(Appointment,id = appointment_id)
    dentists = Dentist.objects.all() 
    treatments = Treatment.objects.all()
    if request.method == 'POST':
        form = AppointmentStatus(request.POST,instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('staff-home')
    return render(request,'staff/edit_appointment.html',{'appointment':appointment,'dentists':dentists,
        'treatments':treatments,})

def add_braces_appointment(request):
    dentists = Dentist.objects.all() 
    treatments = Treatment.objects.all()
    users = User.objects.all()
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointments_data = form.save(commit=False)

            #สร้างนัดหมาย 30 รายการ
            appointments = []
            for i in range(1, 31):  # ตั้งแต่ 1 ถึง 30
                    appointment = Appointment(
                        user=appointments_data.user,
                        treatment=appointments_data.treatment,
                        dentist=appointments_data.dentist,
                        date=None,  # ยังไม่ได้เลือกวัน
                        time_slot=None,  # ยังไม่ได้เลือกเวลา
                        status='Pending Selection',  # รอเลือกวัน/เวลา
                        detail=f'ครั้งที่ {i}'  # กำหนดชื่อเป็น "ครั้งที่ i"
                    )
                    appointments.append(appointment)
            
            # บันทึกในฐานข้อมูล
            Appointment.objects.bulk_create(appointments)
            return redirect('staff-home')
    else:
        form = AppointmentForm()
    return render(request,'staff/add_braces_appointment.html',{
        'form':form,
        'dentists':dentists,
        'treatments':treatments,
        'users':users,})

def dentist_manage(request): 
    dentists = Dentist.objects.all()

    for dentist in dentists:
        dentist.workDaysThai = get_day_name(dentist.workDays)
    # pagination
    paginator = Paginator(dentists,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'staff/dentist_manage.html',{'dentists':dentists,'page_obj':page_obj})

def get_day_name(day_numbers):
    days_map = {
        "1": "จันทร์",
        "2": "อังคาร",
        "3": "พุธ",
        "4": "พฤหัสบดี",
        "5": "ศุกร์",
        "6": "เสาร์",
        "7": "อาทิตย์"
    }
    return ", ".join([days_map.get(day, "") for day in day_numbers.split(",")])    

def add_dentist(request):
    if request.method == 'POST':
        form = DentistForm(request.POST)
        if form.is_valid():
            dentist = form.save(commit=False)  # บันทึกข้อมูลก่อน แต่ไม่ commit
            work_days = request.POST.getlist('workDays')  # ใช้ getlist เพื่อรับค่าหลายค่า
            dentist.workDays = ",".join(work_days)  # เก็บค่า workDays เป็น string ที่แยกด้วยเครื่องหมายจุลภาค
            dentist.save()  # บันทึกข้อมูลทันตแพทย์
            return redirect('dentist-manage') 
        
    return redirect('dentist-manage')

def delete_dentist(request,dentist_id):
    dentist = get_object_or_404(Dentist,id=dentist_id)
    if request.method == 'POST':
        dentist.delete()
        return redirect('dentist-manage')
    return redirect('dentist-manage')

def edit_dentist(request,dentist_id):
    dentist = get_object_or_404(Dentist,id = dentist_id)
    dentist.startTime = dentist.startTime.strftime('%H:%M') if dentist.startTime else ""
    dentist.endTime = dentist.endTime.strftime('%H:%M') if dentist.endTime else ""
    if request.method == 'POST' :
        form = DentistForm(request.POST,instance=dentist)
        if form.is_valid():
             # รับค่า workDays ที่เลือกทั้งหมด
            work_days = request.POST.getlist('workDays')  # ใช้ getlist เพื่อรับค่าหลายค่า
            dentist.workDays = ",".join(work_days)  # เก็บค่า workDays เป็น string ที่แยกด้วยเครื่องหมายจุลภาค
            form.save()
            return redirect('dentist-manage')
    else:
        form = DentistForm(instance=dentist)
    return render(request,'staff/edit_dentist.html',{'dentist':dentist})

def treatment_manage(request): 
    treatments = Treatment.objects.all()
    
    # pagination
    paginator = Paginator(treatments,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'staff/treatment_manage.html',{'treatments':treatments,'page_obj':page_obj})

def add_treatment(request):
    if request.method =="POST" :
        form = TreatmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("treatment-manage")
    return redirect("treatment-manage")

def delete_treatment(request,treatment_id):
    treatment = get_object_or_404(Treatment,id=treatment_id)
    if request.method == 'POST':
        treatment.delete()
        return redirect('treatment-manage')
    return redirect('treatment-manage')

def edit_treatment(request,treatment_id):
    treatment = get_object_or_404(Treatment,id=treatment_id)
    if request.method == "POST" :
        form = TreatmentForm(request.POST,instance = treatment)
        if form.is_valid():
            form.save()
            return redirect("treatment-manage")
    return render(request,"staff/edit_treatment.html",{"treatment":treatment})
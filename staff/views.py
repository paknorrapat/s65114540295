from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import *
from .models import *
from django.http import JsonResponse
from django.db.models import Q
from django.utils.timezone import now
from django.contrib.auth.decorators import user_passes_test,login_required

def is_staff(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_staff, login_url='login')
def staff_home(request):
    search = request.GET.get("search","")
    if search:
        users = User.objects.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search),is_dentist=False,is_manager=False,is_staff=False)
    else :
        users = User.objects.filter(is_dentist=False,is_manager=False,is_staff=False)
    
    dentists = Dentist.objects.all() 
    treatments = Treatment.objects.all()
    
    appointments = Appointment.objects.all()

    treatment_history = TreatmentHistory.objects.all()

    # ฟิลเตอร์นัดหมายที่มีวันที่ตรงกับวันนี้ 
    today = timezone.now().date()
    appointment_today = Appointment.objects.filter(date=today).order_by('time_slot')

    count_appointment_all =appointments.count()
    count_appointment_today =appointment_today.count()
    success_or_fail_today =appointment_today.filter(Q(status="สำเร็จ") | Q(status="ไม่สำเร็จ")).count()

    # pagination
    paginator = Paginator(appointment_today,6) # แบ่งเป็นหน้า 6 รายการต่อหน้า
    appointment_page_number = request.GET.get('appointment_page')
    appointment_page_obj = paginator.get_page(appointment_page_number)

    # pagination 2 add+
    paginator2 = Paginator(users,5) # แบ่งเป็นหน้า 5 รายการต่อหน้า
    user_page_number = request.GET.get('user_page')
    user_page_obj = paginator2.get_page(user_page_number)

    # pagination 3
    paginator3 = Paginator(appointments,5) # แบ่งเป็นหน้า 5 รายการต่อหน้า
    aptall_page_number = request.GET.get('aptall_page')
    aptall_page_obj = paginator3.get_page(aptall_page_number)

    
    return render(request,"staff/staff_home.html",{
        "appointment_today":appointment_today,
        'aptall_page_obj' : aptall_page_obj,
        'appointment_page_obj': appointment_page_obj,
        'user_page_obj': user_page_obj,
        'dentists':dentists,
        'treatments':treatments,
        'users':users,
        'treatment_history':treatment_history,
        'count_appointment_today': count_appointment_today,
        "success_or_fail_today":success_or_fail_today,
        "count_appointment_all":count_appointment_all
        })

@user_passes_test(is_staff, login_url='login')
def appointment_list(request):
    today = now().date()
    dentists = Dentist.objects.all() 
    treatments = Treatment.objects.all()
    appointments = Appointment.objects.all()
  
    # pagination
    paginator = Paginator(appointments,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,"staff/appointment_list.html",{
                                                         "appointments":appointments,
                                                         "page_obj":page_obj,                                       
                                                         'dentists':dentists,
                                                         'treatments':treatments,
                                                         'today': today,})
@user_passes_test(is_staff, login_url='login')
def delete_appointment(request,id):
    appointment = get_object_or_404(Appointment,id=id)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment-list')
    return redirect('appointment-list')

@user_passes_test(is_staff, login_url='login')
def add_appointment(request,user_id):
     # ตรวจสอบว่า user_id ถูกต้องหรือไม่
    user = get_object_or_404(User, id=user_id)
    dentists = Dentist.objects.all() 
    treatments = Treatment.objects.all()

    treatment_history = TreatmentHistory.objects.filter(appointment__user = user_id)

    # ตรวจสอบสถานะของ "ปรึกษาวางแผนจัดฟัน"
    step1_completed = treatment_history.filter(
        appointment__treatment__treatmentName='ปรึกษาวางแผนจัดฟัน', status=True
    ).exists()

    # ตรวจสอบสถานะของ "เคลียร์ช่องปาก"
    step2_completed = treatment_history.filter(
        appointment__treatment__treatmentName='เคลียร์ช่องปาก', status=True
    ).exists()

    # ตรวจสอบสถานะของ "พิมพ์ปากและเอกซเรย์"
    step3_completed = treatment_history.filter(
        appointment__treatment__treatmentName='พิมพ์ปากและเอกซเรย์', status=True
    ).exists()

    # ตรวจสอบสถานะของ "ติดเครื่องมือ"
    step4_total = 30  # จำนวนครั้งที่ต้องการ
    step4_count = treatment_history.filter(
        appointment__treatment__treatmentName='ติดเครื่องมือ', status=True
    ).count()
    step4_completed = step4_count >= step4_total

    # ตรวจสอบสถานะของ "ถอดเครื่องมือ"
    step5_completed = treatment_history.filter(
        appointment__treatment__treatmentName='ถอดเครื่องมือ', status=True
    ).exists()
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = user
            appointment.save()

             # ตรวจสอบว่าการรักษาคือ "ติดเครื่องมือ"
            if appointment.treatment.treatmentName == "ติดเครื่องมือ":
                # กำหนดรายละเอียดให้กับ appointment แรก
                appointment.detail = "ครั้งที่ 1"
                appointment.status = "รอการนัดหมาย"
                appointment.save()
                # สร้างนัดหมาย 29 รายการ
                appointments = []
                for i in range(2, 31):  # ตั้งแต่ 2 ถึง 30
                    appointments.append(Appointment(
                        user=user,
                        treatment=appointment.treatment,
                        dentist=appointment.dentist,
                        date=None,  # ยังไม่ได้เลือกวัน
                        time_slot=None,  # ยังไม่ได้เลือกเวลา
                        status='รอการนัดหมาย',  # สถานะเริ่มต้น
                        detail=f'ครั้งที่ {i}'  # ระบุรายละเอียดเป็น "ครั้งที่ i"
                    ))

                # บันทึกในฐานข้อมูล
                Appointment.objects.bulk_create(appointments)

            return redirect('staff-home')
    else:
        form = AppointmentForm()
    return render(request,'staff/add_appointment.html',{'user': user,
                                                         'dentists':dentists,
                                                        'treatments':treatments,
                                                        "step1_completed": step1_completed,
                                                         "step2_completed": step2_completed,
                                                         "step3_completed": step3_completed,
                                                         "step4_completed": step4_completed,
                                                         "step4_count": step4_count,
                                                         "step4_total": step4_total,
                                                         "step5_completed": step5_completed,
                                                        })

@user_passes_test(is_staff, login_url='login')
def update_appointment(request,appointment_id):
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


@user_passes_test(is_staff, login_url='login')
def dentist_manage(request): 
    users = User.objects.filter(is_dentist=True, dentist__workDays__isnull=False).exclude(dentist__workDays='')
    dentists = User.objects.filter(is_dentist=True)
    for user in users:
        # แปลง workDays เป็นชื่อวันในภาษาไทย
        user.workDaysThai = get_day_name(user.dentist.workDays)

    # pagination
    paginator = Paginator(users, 10)  # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'staff/dentist_manage.html', {'users': users, 'page_obj': page_obj,'dentists':dentists})

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
   
@user_passes_test(is_staff, login_url='login')
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

@user_passes_test(is_staff, login_url='login')
def delete_dentist(request,dentist_id):
    dentist = get_object_or_404(Dentist,id=dentist_id)
    if request.method == 'POST':
        dentist.delete()
        return redirect('dentist-manage')
    return redirect('dentist-manage')

@user_passes_test(is_staff, login_url='login')
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

@user_passes_test(is_staff, login_url='login')
def treatment_manage(request): 
    treatments = Treatment.objects.all()
    extras = Extra.objects.all()
    
    # pagination
    paginator = Paginator(treatments,5) # แบ่งเป็นหน้า 5 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # pagination
    paginator2 = Paginator(extras,5) # แบ่งเป็นหน้า 5 รายการต่อหน้า
    page_number_extra = request.GET.get('page_extra')
    page_obj_extra = paginator2.get_page(page_number_extra)

    return render(request,'staff/treatment_manage.html',{'treatments':treatments,'page_obj':page_obj,'extras':extras,'page_obj_extra':page_obj_extra})

@user_passes_test(is_staff, login_url='login')
def add_treatment(request):
    if request.method =="POST" :
        form = TreatmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("treatment-manage")
    return redirect("treatment-manage")

@user_passes_test(is_staff, login_url='login')
def delete_treatment(request,treatment_id):
    treatment = get_object_or_404(Treatment,id=treatment_id)
    if request.method == 'POST':
        treatment.delete()
        return redirect('treatment-manage')
    return redirect('treatment-manage')

@user_passes_test(is_staff, login_url='login')
def edit_treatment(request,treatment_id):
    treatment = get_object_or_404(Treatment,id=treatment_id)
    if request.method == "POST" :
        form = TreatmentForm(request.POST,instance = treatment)
        if form.is_valid():
            form.save()
            return redirect("treatment-manage")
    return render(request,"staff/edit_treatment.html",{"treatment":treatment})

@user_passes_test(is_staff, login_url='login')
def add_extra(request):
    if request.method =="POST" :
        form = ExtraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("treatment-manage")
    return redirect("treatment-manage")

@user_passes_test(is_staff, login_url='login')
def delete_extra(request,extra_id):
    extra = get_object_or_404(Extra,id=extra_id)
    if request.method == 'POST':
        extra.delete()
        return redirect('treatment-manage')
    return redirect('treatment-manage')

@user_passes_test(is_staff, login_url='login')
def edit_extra(request,extra_id):
    extra = get_object_or_404(Extra,id=extra_id)
    if request.method == "POST" :
        form = ExtraForm(request.POST,instance = extra)
        if form.is_valid():
            form.save()
            return redirect("treatment-manage")
    return render(request,"staff/edit_extra.html",{"extra":extra})

@login_required
def member_info(request):
    search = request.GET.get("search","")
    if search:
        users = User.objects.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search),is_dentist=False,is_manager=False,is_staff=False)
    else :
        users = User.objects.filter(is_dentist=False,is_manager=False,is_staff=False)

    # pagination 2
    paginator2 = Paginator(users,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    user_page_number = request.GET.get('user_page')
    user_page_obj = paginator2.get_page(user_page_number)

    return render(request,"staff/member_info.html",{"users":users,"user_page_obj":user_page_obj})



from django.shortcuts import render,redirect,get_object_or_404
from Sparky.models import *
from .forms import AppointmentForm
from django.http import JsonResponse
from datetime import datetime,date,timedelta
import json
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q,Sum
from django.utils.timezone import now
from django.contrib.auth.decorators import user_passes_test,login_required
from django.http import HttpResponseForbidden

def is_member(user):
    return user.is_authenticated 
# Create your views here.
@user_passes_test(is_member, login_url='login')
def member_home(request):
    search = request.GET.get("search","")
    if search:
        dentists = Dentist.objects.filter(
        Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search)
    )
    else:
        dentists = Dentist.objects.all()

    for dentist in dentists:
        # แปลง workDays เป็นชื่อวันในภาษาไทย
        dentist.workDaysThai = get_day_name(dentist.workDays)

    treatments = Treatment.objects.all()
    
    appointments = Appointment.objects.filter(user = request.user)

    treatment_history = TreatmentHistory.objects.all()
    
    # ฟิลเตอร์นัดหมายที่มีวันที่ตรงกับวันนี้ 
    today = timezone.now().date()
    appointment_today = Appointment.objects.filter(user = request.user,date=today).order_by('time_slot')

    count_appointment_all =appointments.count()
    count_appointment_today =appointment_today.count()
    success_or_fail_today =appointment_today.filter(Q(status="สำเร็จ") | Q(status="ไม่สำเร็จ")).count()

    # pagination
    paginator = Paginator(appointment_today,5) # แบ่งเป็นหน้า 5 รายการต่อหน้า
    appointment_page_number = request.GET.get('appointment_page')
    appointment_page_obj = paginator.get_page(appointment_page_number)

    # pagination 2
    paginator2 = Paginator(dentists,5) # แบ่งเป็นหน้า 5 รายการต่อหน้า
    user_page_number = request.GET.get('user_page')
    user_page_obj = paginator2.get_page(user_page_number)

    # pagination 3
    paginator3 = Paginator(appointments,5) # แบ่งเป็นหน้า 5 รายการต่อหน้า
    aptall_page_number = request.GET.get('aptall_page')
    aptall_page_obj = paginator3.get_page(aptall_page_number)

    return render(request,"member/member_home.html",{
        "appointment_today":appointment_today,
        'aptall_page_obj' : aptall_page_obj,
        'appointment_page_obj': appointment_page_obj,
        'user_page_obj': user_page_obj,
        'dentists':dentists,
        'treatments':treatments,
        'treatment_history':treatment_history,
        'count_appointment_today': count_appointment_today,
        "success_or_fail_today":success_or_fail_today,
        "count_appointment_all":count_appointment_all,
    })

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

@login_required(login_url='login')
def t_history(request,user_id):
    t_history = TreatmentHistory.objects.filter(appointment__user = user_id)
    # ตรวจสอบว่าเป็นเจ้าของข้อมูล, staff, หรือ dentist
    if request.user.id != user_id and not request.user.is_staff and not request.user.is_dentist:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์เข้าถึงประวัติการรักษานี้")
    
     # pagination
    paginator = Paginator(t_history,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"member/t_history.html",{'page_obj':page_obj})

@login_required(login_url='login')
def braces_progress(request,user_id):
    treatment_history = TreatmentHistory.objects.filter(appointment__user = user_id)
    braces = treatment_history.filter(appointment__treatment__is_braces=True)

     # ตรวจสอบว่าเป็นเจ้าของข้อมูล, staff, หรือ dentist
    if request.user.id != user_id and not request.user.is_staff and not request.user.is_dentist:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์เข้าถึงสถานะการจัดฟันนี้")
    
     # pagination
    paginator = Paginator(braces,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # คำนวณค่าใช้จ่ายทั้งหมดสำหรับการจัดฟัน
    total_cost = treatment_history.filter(appointment__treatment__is_braces=True).aggregate(total=Sum('cost'))['total'] or 0

    # ค่าใช้จ่ายของ "เคลียร์ช่องปาก"
    clear_cost = treatment_history.filter(
        appointment__treatment__treatmentName='เคลียร์ช่องปาก'
    ).aggregate(total=Sum('cost'))['total'] or 0

    max_cost = 40000 + clear_cost # ค่าใช้จ่ายรวมทั้งหมด
    percentage_paid = min((total_cost / max_cost) * 100, 100)  # จำกัดไม่เกิน 100%

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

    
    return render(request,"member/braces_progress.html",{"treatment_history": treatment_history,
                                                         "step1_completed": step1_completed,
                                                         "step2_completed": step2_completed,
                                                         "step3_completed": step3_completed,
                                                         "step4_completed": step4_completed,
                                                         "step4_count": step4_count,
                                                         "step4_total": step4_total,
                                                         "step5_completed": step5_completed,
                                                         "total_cost":total_cost,
                                                         "braces":braces,
                                                         'page_obj':page_obj,
                                                         "percentage_paid": round(percentage_paid, 2),
                                                         "max_cost": max_cost,
                                                         })

@user_passes_test(is_member, login_url='login')
def delete_appointment_member(request,id):
    appointment = get_object_or_404(Appointment,id=id)
    if request.method == 'POST':
        appointment.delete()
        return redirect('member-home')
    return redirect('member-home')

@user_passes_test(is_member, login_url='login')
def appointment_view(request,dentist_id):
    dentist = get_object_or_404(Dentist, id=dentist_id) 
    treatments = Treatment.objects.all()
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.dentist = dentist  # กำหนด Dentist ที่เลือก
            appointment.save()
            return redirect('member-home')
    else:
        form = AppointmentForm()
    
    return render(request,'appointment/appointment_form.html',{'form':form,'dentist':dentist,'treatments':treatments})

@login_required(login_url='login')
def get_time_slots(request):
    date_str = request.GET.get('date')
    dentist_id = request.GET.get('dentist_id')  # รับ dentist_id เพื่อกรองเวลาสำหรับทันตแพทย์เฉพาะ
    if not date_str:
        return JsonResponse({'slots':[]})
    
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    dentist = Dentist.objects.filter(id=dentist_id).first()
    if not dentist:
        return JsonResponse({'slots': []})
    
    # ตรวจสอบว่าวันที่เลือกอยู่ในวันทำงานของทันตแพทย์หรือไม่
    selected_weekday = str(selected_date.isoweekday())  # แปลงเป็นตัวเลข (1=จันทร์, ..., 7=อาทิตย์)
    work_days = dentist.workDays.split(',')  # แปลง workDays เป็น list
    if selected_weekday not in work_days:
        return JsonResponse({'slots': []})  # หากวันไม่อยู่ในวันทำงาน ให้คืนค่าช่องว่าง

    # ช่วงเวลาทำงานของทันตแพทย์
    start_time = dentist.startTime  # เวลาเริ่มทำงาน
    end_time = dentist.endTime      # เวลาสิ้นสุดการทำงาน
    
     # กำหนด time slots (เช่น ทุก 1 ชั่วโมง)
    time_slots = []
    current_time = datetime.combine(selected_date, start_time)
    while current_time.time() < end_time:
        time_slots.append(current_time.time())
        current_time += timedelta(minutes=60)  # เพิ่มทีละ 60 นาที

    # ตรวจสอบ slot ที่ว่าง
    booked_appointments = Appointment.objects.filter(date=selected_date,dentist_id = dentist_id).values_list('time_slot',flat=True)
    available_slots = [slot.strftime('%H:%M') for slot in time_slots if slot not in booked_appointments]

    return JsonResponse({'slots': available_slots})

@login_required(login_url='login')
def calendar_view(request):
    appointments = Appointment.objects.all().values('date', 'time_slot', 'treatment__treatmentName','dentist__user__title','dentist__user__first_name', 
        'dentist__user__last_name')
    events = []
    
    for appointment in appointments:
        # ตรวจสอบว่า time_slot มีค่าที่ถูกต้อง
        if appointment['time_slot']:
            # สร้าง start โดยไม่เพิ่ม :00 ที่เกิน
            events.append({
                'title': f'{appointment["treatment__treatmentName"]} : {appointment["dentist__user__title"]}{appointment["dentist__user__first_name"]} {appointment["dentist__user__last_name"]}',
                'start': f'{appointment["date"]}T{appointment["time_slot"]}', 
                'allDay': False,
            })
    
    events_json = json.dumps(events)  # แปลง events เป็น JSON string
    return render(request, 'appointment/calendar.html', {'events': events_json})

@user_passes_test(is_member, login_url='login')
def select_appointment_date(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

    if request.method == 'POST':
        selected_date = request.POST.get('date')
        selected_time = request.POST.get('time_slot')

        # บันทึกวันและเวลาที่เลือก
        appointment.date = selected_date
        appointment.time_slot = selected_time
        appointment.status = 'รอดำเนินการ'  # เปลี่ยนสถานะเป็นยืนยัน
        appointment.save()

        return redirect('appointment-all')  # ไปยังหน้ารายการนัดหมายของ Member

    return render(request, 'member/select_appointment_date.html', {
        'appointment': appointment
    })

@user_passes_test(is_member, login_url='login')
def delete_appointment_member(request,id):
    appointment = get_object_or_404(Appointment,id=id)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment-all')
    return redirect('appointment-all')

@user_passes_test(is_member, login_url='login')
def edit_appointment_member(request,id):
    appointment = get_object_or_404(Appointment,id = id)
    dentists = Dentist.objects.all() 
    treatments = Treatment.objects.all()
    if request.method == 'POST':
        form = AppointmentForm(request.POST,instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appointment-all')
        else:
            form = AppointmentForm(instance=appointment)
    return render(request,'member/edit_appointment_member.html',{'appointment':appointment,'dentists':dentists,
        'treatments':treatments,})

@user_passes_test(is_member, login_url='login')
def appointment_all(request):
    dentists = Dentist.objects.all() 
    treatments = Treatment.objects.all()
    appointments = Appointment.objects.filter(user = request.user)

    today = now().date()
    # pagination
    paginator = Paginator(appointments,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,"member/appointment_all.html",{
                                                         "appointments":appointments,
                                                         "page_obj":page_obj,                                       
                                                         'dentists':dentists,
                                                         'treatments':treatments,
                                                         'today': today,})

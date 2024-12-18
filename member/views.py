from django.shortcuts import render,redirect,get_object_or_404
from .models import Appointment,Dentist,Treatment
from .forms import AppointmentForm
from django.http import JsonResponse
from datetime import datetime,date,timedelta
import json
from django.core.paginator import Paginator

# Create your views here.
def member_home(request):
    today = date.today()
    appointments = Appointment.objects.filter(user=request.user)
    appointments_select = Appointment.objects.filter(status='Pending Selection')  # กรองเฉพาะสถานะ Pending Selection
    appointments_today = Appointment.objects.filter(user=request.user,date=today)

    # pagination
    paginator = Paginator(appointments,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,"member/member_home.html",{'appointments':appointments,'appointments_today':appointments_today,'appointments_select':appointments_select,'page_obj': page_obj,'today': today,})

def delete_appointment_member(request,id):
    appointment = get_object_or_404(Appointment,id=id)
    if request.method == 'POST':
        appointment.delete()
        return redirect('member-home')
    return redirect('member-home')


def appointment_view(request):
    dentists = Dentist.objects.all() 
    treatments = Treatment.objects.all()
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            return redirect('member-home')
    else:
        form = AppointmentForm()
    
    return render(request,'appointment/appointment_form.html',{'form':form,'dentists':dentists,'treatments':treatments})

def appointment_success_view(request):
    return render(request,'appointment/appointment_success.html')

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

def calendar_view(request):
    appointments = Appointment.objects.all().values('date', 'time_slot', 'treatment__treatmentName','dentist__dentistName')
    events = []
    
    for appointment in appointments:
        # ตรวจสอบว่า time_slot มีค่าที่ถูกต้อง
        if appointment['time_slot']:
            # สร้าง start โดยไม่เพิ่ม :00 ที่เกิน
            events.append({
                'title': f'{appointment["treatment__treatmentName"]} : {appointment["dentist__dentistName"]} ',
                'start': f'{appointment["date"]}T{appointment["time_slot"]}', 
                'allDay': False,
            })
    
    events_json = json.dumps(events)  # แปลง events เป็น JSON string
    return render(request, 'appointment/calendar.html', {'events': events_json})

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

        return redirect('member-home')  # ไปยังหน้ารายการนัดหมายของ Member

    return render(request, 'member/select_appointment_date.html', {
        'appointment': appointment
    })

def delete_appointment_member(request,id):
    appointment = get_object_or_404(Appointment,id=id)
    if request.method == 'POST':
        appointment.delete()
        return redirect('member-home')
    return redirect('member-home')

def edit_appointment_member(request,id):
    appointment = get_object_or_404(Appointment,id = id)
    dentists = Dentist.objects.all() 
    treatments = Treatment.objects.all()
    if request.method == 'POST':
        form = AppointmentForm(request.POST,instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('member-home')
        else:
            form = AppointmentForm(instance=appointment)
    return render(request,'member/edit_appointment_member.html',{'appointment':appointment,'dentists':dentists,
        'treatments':treatments,})

from django.shortcuts import render,redirect,get_object_or_404
from Sparky.models import *
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import *
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test,login_required
from datetime import datetime
def is_dentist(user):
    return user.is_authenticated and user.is_dentist

@user_passes_test(is_dentist, login_url='login')
def dentist_home(request):
    # ฟิลเตอร์นัดหมายที่มีวันที่ตรงกับวันนี้ 
    today = timezone.now().date()
    appointment_today = Appointment.objects.filter(date=today,dentist=request.user.dentist).order_by('time_slot')
    appointments = Appointment.objects.filter(dentist=request.user.dentist)

    count_appointment_all =appointments.count()
    count_appointment_today =appointment_today.count()
    success_or_fail_today =appointment_today.filter(Q(status="สำเร็จ") | Q(status="ไม่สำเร็จ")).count()
    # pagination วันนี้
    paginator = Paginator(appointment_today,5) # แบ่งเป็นหน้า 5 รายการต่อหน้า
    appointment_page_number = request.GET.get('appointment_page')
    appointment_page_obj = paginator.get_page(appointment_page_number)

    #รับค่า filter จาก dropdown
    selected_day = request.GET.get('day')
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    selected_status = request.GET.get('status')  # รับค่าของ status

    search = request.GET.get("search","")
    # กรองข้อมูล
    if search:
        appointments = appointments.filter(Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search))
    if selected_day:
        appointments = appointments.filter(date__day=selected_day)
    if selected_month:
        appointments = appointments.filter(date__month=selected_month)
    if selected_year:
        appointments = appointments.filter(date__year=selected_year)
    if selected_status:  # กรองตามสถานะ
        appointments = appointments.filter(status=selected_status) 

    # จัดการ Query Parameters (ลบ key 'page')
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    
    #ข้อมูล dropdown
    days = list(range(1,32))
    # ข้อมูลเดือน (mapping)
    months = [
    (1, "มกราคม"), (2, "กุมภาพันธ์"), (3, "มีนาคม"), (4, "เมษายน"),
    (5, "พฤษภาคม"), (6, "มิถุนายน"), (7, "กรกฎาคม"), (8, "สิงหาคม"),
    (9, "กันยายน"), (10, "ตุลาคม"), (11, "พฤศจิกายน"), (12, "ธันวาคม")
    ]
    years =range(2021,datetime.now().year + 1)

    statuses = [
        ('รอดำเนินการ', 'รอดำเนินการ'),  
        ('สำเร็จ', 'สำเร็จ'),         
        ('ไม่สำเร็จ', 'ไม่สำเร็จ'),
    ]
    # pagination ทั้งหมด
    paginator = Paginator(appointments,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"dentist/dentist_home.html",{'appointment_page_obj': appointment_page_obj,
                                                       'page_obj':page_obj,
                                                       'count_appointment_today': count_appointment_today,
                                                       "success_or_fail_today":success_or_fail_today,
                                                       "count_appointment_all":count_appointment_all,
                                                       "days": days,
                                                       "months": months,
                                                       "years": years,
                                                       "statuses": statuses, 
                                                       "selected_day": selected_day,
                                                       "selected_month": selected_month,
                                                       "selected_year": selected_year,
                                                       "selected_status": selected_status,
                                                       "query_params": query_params.urlencode()  # ส่ง Query Parameters ที่จัดการแล้วไปยัง Template 
                                                       })

@user_passes_test(is_dentist, login_url='login')
def treatment_history(request):
     # ฟิลเตอร์นัดหมายที่มีวันที่ตรงกับวันนี้ 
    today = timezone.now().date()
    appointment_today = Appointment.objects.filter(date=today,dentist=request.user.dentist,status='สำเร็จ').order_by('time_slot')
    appointments = Appointment.objects.filter(dentist=request.user.dentist,status='สำเร็จ',treatmenthistory__status=True)

    t_history = Appointment.objects.filter(dentist=request.user.dentist,status='สำเร็จ')

    count_th_all =appointments.count()
    count_th_today =appointment_today.count()
    success_today =appointment_today.filter(treatmenthistory__status=True).count()

    # pagination
    paginator = Paginator(appointment_today,5) # แบ่งเป็นหน้า 5 รายการต่อหน้า
    appointment_page_number = request.GET.get('appointment_page')
    appointment_page_obj = paginator.get_page(appointment_page_number)

    # pagination
    paginator = Paginator(t_history,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"dentist/treatment_history.html",{'appointment_page_obj': appointment_page_obj,
                                                            'page_obj':page_obj,
                                                            'count_th_all':count_th_all,
                                                            'count_th_today':count_th_today,
                                                            'success_today':success_today,
                                                    
                                                            })
@user_passes_test(is_dentist, login_url='login')
def t_history_all(request):
    treatmenthistorys = TreatmentHistory.objects.filter(appointment__dentist=request.user.dentist,status=True).order_by('-appointment__date')
    
    #รับค่า filter จาก dropdown
    selected_day = request.GET.get('day')
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
 
    search = request.GET.get("search","")
    # กรองข้อมูล
    if search:
        treatmenthistorys = treatmenthistorys.filter(Q(appointment__user__first_name__icontains=search) | Q(appointment__user__last_name__icontains=search))
    if selected_day:
        treatmenthistorys = treatmenthistorys.filter(appointment__date__day=selected_day)
    if selected_month:
        treatmenthistorys = treatmenthistorys.filter(appointment__date__month=selected_month)
    if selected_year:
        treatmenthistorys = treatmenthistorys.filter(appointment__date__year=selected_year)

    # จัดการ Query Parameters (ลบ key 'page')
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')

    # pagination
    paginator = Paginator(treatmenthistorys,10) # แบ่งเป็นหน้า 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    #ข้อมูล dropdown
    days = list(range(1,32))
    # ข้อมูลเดือน (mapping)
    months = [
    (1, "มกราคม"), (2, "กุมภาพันธ์"), (3, "มีนาคม"), (4, "เมษายน"),
    (5, "พฤษภาคม"), (6, "มิถุนายน"), (7, "กรกฎาคม"), (8, "สิงหาคม"),
    (9, "กันยายน"), (10, "ตุลาคม"), (11, "พฤศจิกายน"), (12, "ธันวาคม")
    ]
    years =range(2021,datetime.now().year + 1)

    return render(request,"dentist/t_history_all.html",{'page_obj':page_obj,
                                                        "days": days,
                                                        "months": months,
                                                        "years": years,                                                 
                                                        "selected_day": selected_day,
                                                        "selected_month": selected_month,
                                                        "selected_year": selected_year,
                                                        "query_params": query_params.urlencode()  # ส่ง Query Parameters ที่จัดการแล้วไปยัง Template
                                                        })

@user_passes_test(is_dentist, login_url='login')
def add_treatment_history(request, apt_id):
    appointment = get_object_or_404(Appointment, id=apt_id)
    extras = Extra.objects.all()
    treatments = Treatment.objects.all()

    if request.method == "POST":
        form = TreatmentHistoryForm(request.POST)
        if form.is_valid():
            treatmenthistory = form.save(commit=False)
            treatmenthistory.appointment = appointment
            treatmenthistory.status = True
            treatmenthistory.save()

            return redirect("treatment-history")
        
    return render(request, 'dentist/add_t_history.html', {
        'extras': extras,
        'appointment': appointment,
        'treatments': treatments,
    })

@user_passes_test(is_dentist, login_url='login')
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
from django.shortcuts import render,get_object_or_404,redirect
from Sparky.models import User,Appointment,TreatmentHistory,Profile
from django.core.paginator import Paginator
from .forms import *
from django.db.models import Q,Count,Sum
from datetime import datetime
from django.db.models.functions import TruncMonth, ExtractHour, ExtractWeekDay
from django.utils.timezone import now,localtime
from django.contrib.auth.decorators import user_passes_test,login_required
from django.contrib import messages

def is_manager(user):
    return user.is_authenticated and user.is_manager

def calculate_age(birth_date):
    today = datetime.now()
    return today.year - birth_date.year - ((today.month,today.day)<(birth_date.month, birth_date.day))

@user_passes_test(is_manager, login_url='login')
def dashboard(request):
    # รับค่า GET parameter
    selected_year = request.GET.get('year', None)
    selected_month = request.GET.get('month', None)
    selected_day = request.GET.get('day', None)

    # ตรวจสอบว่าค่าที่รับมาเป็นตัวเลขหรือไม่
    if not selected_year or not selected_year.isdigit():
        selected_year = datetime.now().year  # ค่าเริ่มต้นเป็นปีปัจจุบัน
    else:
        selected_year = int(selected_year)

    # ตรวจสอบเดือน (ค่าเริ่มต้นเป็น None เพื่อหมายถึงทั้งปี)
    if selected_month and selected_month.isdigit():
        selected_month = int(selected_month)
    else:
        selected_month = None

    # ตรวจสอบวัน (ค่าเริ่มต้นเป็น None เพื่อหมายถึงทั้งเดือน)
    if selected_day and selected_day.isdigit():
        selected_day = int(selected_day)
    else:
        selected_day = None

    # กรองข้อมูลตามปี เดือน และวัน (ถ้ามี)
    appointment_filter = {'date__year': selected_year}
    if selected_month:
        appointment_filter['date__month'] = selected_month
    if selected_day:
        appointment_filter['date__day'] = selected_day

    # ข้อมูลเบื้องต้น
    patients_count = User.objects.filter(is_staff=False, is_dentist=False, is_manager=False, is_superuser=False).count()
    dentists_count = User.objects.filter(is_dentist=True).count()
    staffs_count = User.objects.filter(is_staff=True, is_superuser=False).count()

    # นับผู้ป่วยใหม่และเก่าในปีที่เลือก
    year_start = datetime(datetime.now().year, 1, 1)
    new_patients = User.objects.filter(
        is_staff=False, is_dentist=False, is_manager=False, is_superuser=False, date_joined__gte=year_start
    ).count()
    old_patients = User.objects.filter(
        is_staff=False, is_dentist=False, is_manager=False, is_superuser=False, date_joined__lt=year_start
    ).count()
    
     # นับจำนวนการนัดหมายตามวันในสัปดาห์
    appointments_by_day = (
        Appointment.objects.filter(**appointment_filter)
        .annotate(day_of_week=ExtractWeekDay('date'))
        .values('day_of_week')
        .annotate(total=Count('id'))
        .order_by('day_of_week')
    )

     # นับจำนวนการนัดหมายตามชั่วโมง
    appointments_by_hour = (
        Appointment.objects.filter(**appointment_filter)
        .annotate(hour=ExtractHour('time_slot'))
        .values('hour')
        .annotate(total=Count('id'))
        .order_by('hour')
    )

    #คำนวณช่วงอายุ
    age_ranges = [(0, 18), (19, 30), (31, 45), (46, 60), (61, 100)]
    age_range_labels = ["0-18", "19-30", "31-45", "46-60", "61+"]
    patients_by_age = []
    for i, age_range in enumerate(age_ranges):
        count = Profile.objects.filter(
            user__is_superuser=False,
            user__is_manager=False,
            user__is_dentist=False,
            user__is_staff=False,
            birthDate__isnull=False,
            birthDate__lte=datetime.now().replace(year=datetime.now().year - age_range[0]),
            birthDate__gt=datetime.now().replace(year=datetime.now().year - age_range[1] - 1),
        ).count()
        patients_by_age.append({'range': age_range_labels[i], 'total': count})

     # นับจำนวนผู้ป่วยตามเพศ
        patients_by_gender = (
            Profile.objects.filter(
                user__is_superuser=False,
                user__is_manager=False,
                user__is_dentist=False,
                user__is_staff=False,
            )
            .values('gender')
            .annotate(total=Count('id'))
            .order_by('gender')
        )

        # นับจำนวนการนัดหมายตามทันตแพทย์
        dentist_workload = (
            Appointment.objects.filter(**appointment_filter)
            .values('dentist__user__title', 'dentist__user__first_name', 'dentist__user__last_name')
            .annotate(total_appointments=Count('id'))
            .order_by('-total_appointments')
        )

        # ส่งค่าปีที่เลือกไปยัง Template
        years = range(2024, datetime.now().year + 1)
        
        months = [
        (1, "มกราคม"), (2, "กุมภาพันธ์"), (3, "มีนาคม"), (4, "เมษายน"),
        (5, "พฤษภาคม"), (6, "มิถุนายน"), (7, "กรกฎาคม"), (8, "สิงหาคม"),
        (9, "กันยายน"), (10, "ตุลาคม"), (11, "พฤศจิกายน"), (12, "ธันวาคม")
        ]

        days = range(1, 32)

    return render(request,"manager/dashboard.html",{                                                                                                           
                                                    'patients_by_gender': patients_by_gender,
                                                    'patients_by_age': patients_by_age,
                                                    'dentist_workload': dentist_workload,
                                                    'patients_count': patients_count,
                                                    'dentists_count': dentists_count,
                                                    'staffs_count': staffs_count,
                                                    'new_patients': new_patients,
                                                    'old_patients': old_patients,
                                                    'appointments_by_day': appointments_by_day,
                                                    'appointments_by_hour': appointments_by_hour,
                                                    'years': years,  # ตัวเลือกปี
                                                    'selected_year': selected_year,  # ปีที่เลือก
                                                    'months': months,
                                                    'selected_month': selected_month,
                                                    'days': days,
                                                    'selected_day': selected_day, 
                                                    })

@user_passes_test(is_manager, login_url='login')
def second_dashboard(request):

    today_date = localtime(now()).date()  
    current_date = now()
    current_month = current_date.month
    current_year = current_date.year

    total_income_today = TreatmentHistory.objects.filter(appointment__date=today_date ).aggregate(Sum('cost'))['cost__sum'] or 0
    total_income_month = TreatmentHistory.objects.filter(appointment__date__year=current_year,appointment__date__month=current_month,).aggregate(Sum('cost'))['cost__sum'] or 0
    total_income_all = TreatmentHistory.objects.filter(appointment__date__year=current_year).aggregate(Sum('cost'))['cost__sum'] or 0

    # รับค่าปี, เดือน, และวันจาก GET parameter
    selected_year = request.GET.get('year', None)
    selected_month = request.GET.get('month', None)
    selected_day = request.GET.get('day', None)
  
    # ตรวจสอบปี (ค่าเริ่มต้นเป็นปีปัจจุบัน)
    if not selected_year or not selected_year.isdigit():
        selected_year = now().year
    else:
        selected_year = int(selected_year)

    # ตรวจสอบเดือน (ค่าเริ่มต้นเป็น None เพื่อหมายถึงทั้งปี)
    if selected_month and selected_month.isdigit():
        selected_month = int(selected_month)
    else:
        selected_month = None

    # ตรวจสอบวัน (ค่าเริ่มต้นเป็น None เพื่อหมายถึงทั้งเดือน)
    if selected_day and selected_day.isdigit():
        selected_day = int(selected_day)
    else:
        selected_day = None

  
    # สร้างตัวกรองสำหรับ TreatmentHistory
    date_filter = {'appointment__date__year': selected_year}
    if selected_month:
        date_filter['appointment__date__month'] = selected_month
    if selected_day:
        date_filter['appointment__date__day'] = selected_day

    # รายได้รวมตามเดือน
    revenue_by_month = (
        TreatmentHistory.objects.filter(**date_filter)
        .annotate(month=TruncMonth('appointment__date'))
        .values('month')
        .annotate(total_revenue=Sum('cost'))
        .order_by('month')
    )

    # รายได้รวมแยกตามประเภทการรักษา
    revenue_by_treatment = (
        TreatmentHistory.objects.filter(**date_filter)
        .values('appointment__treatment__treatmentName')
        .annotate(total_revenue=Sum('cost'))
        .order_by('-total_revenue')
    )

    # การนับจำนวนการนัดหมายตามประเภทการรักษา
    treatment_popularity = (
        Appointment.objects.filter(status="สำเร็จ",date__year = selected_year)
        .values('treatment__treatmentName')
        .annotate(total_appointments=Count('id'))
        .order_by('-total_appointments')  # เรียงตามจำนวนการนัดหมายมากไปน้อย
    )

     # สร้างตัวกรองสำหรับ Appointment
    apt_filter = {'date__year': selected_year}
    if selected_month:
        apt_filter['date__month'] = selected_month
    if selected_day:
        apt_filter['date__day'] = selected_day

    # กรองการนัดหมายตามปี, เดือน, และวัน
    appointments = Appointment.objects.filter(**apt_filter,
                                              date__isnull=False,      # กรองเฉพาะรายการที่มีวัน
                                              time_slot__isnull=False  # กรองเฉพาะรายการที่มีเวลา
                                              )
    appointments_by_status = appointments.values('status').annotate(total=Count('id'))
    appointments_by_month = appointments.annotate(month=TruncMonth('date')).values('month').annotate(total=Count('id')).order_by('month')

     # แมปตัวเลขเดือนเป็นชื่อเดือนภาษาไทย
    month_names = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                   "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    
    for month in revenue_by_month:
        month_number = month['month'].month
        month['month_name'] = month_names[month_number - 1]

    for month in appointments_by_month:
        month_number = month['month'].month
        month['month_name'] = month_names[month_number - 1]

    # สร้างตัวเลือกปี, เดือน, และวัน
    years = range(2024, now().year + 1)
    months = [
        (1, "มกราคม"), (2, "กุมภาพันธ์"), (3, "มีนาคม"), (4, "เมษายน"),
        (5, "พฤษภาคม"), (6, "มิถุนายน"), (7, "กรกฎาคม"), (8, "สิงหาคม"),
        (9, "กันยายน"), (10, "ตุลาคม"), (11, "พฤศจิกายน"), (12, "ธันวาคม")
    ]
    days = range(1, 32)
    context = {
        'revenue_by_month': revenue_by_month,
        'revenue_by_treatment':revenue_by_treatment,
        'treatment_popularity': treatment_popularity,
        'appointments_by_month': appointments_by_month,
        'appointments_by_status': appointments_by_status,
        'total_income_today': total_income_today,
        'total_income_month': total_income_month,
        'total_income_all': total_income_all,
        'years': years,
        'months': months,
        'days': days,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_day': selected_day,
        
    }
    return render(request,'manager/second_dashboard.html',context)

@user_passes_test(is_manager, login_url='login')
def user_list(request):
    search = request.GET.get("search","")
    if search:
        users = User.objects.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search),is_superuser=False,is_manager=False,is_dentist=False,is_staff=False)
    else :
        users = User.objects.filter(is_superuser=False,is_manager=False,is_dentist=False,is_staff=False)

    #paginator
    paginator = Paginator(users,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"manager/user_list.html",{"page_obj":page_obj})

@user_passes_test(is_manager, login_url='login')
def update_role(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        role = request.POST.get("role")
        user = get_object_or_404(User, id=user_id)
        if role == "Staff":
            user.is_staff = True
            user.is_dentist = False
            user.save()
            messages.success(request, 'เปลี่ยนสถานะสำเร็จ')
            return redirect('staff-list')
        elif role == "Dentist":
            user.is_staff = False
            user.is_dentist = True
            user.save()
            messages.success(request, 'เปลี่ยนสถานะสำเร็จ')
            return redirect('dentist-list')
        else:  # Member
            user.is_staff = False
            user.is_dentist = False
            user.save()
            messages.success(request, 'เปลี่ยนสถานะสำเร็จ')
            return redirect('user-list')

@user_passes_test(is_manager, login_url='login')
def dentist_list(request):
    users = User.objects.filter(is_dentist=True)
    #paginator
    paginator = Paginator(users,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"manager/dentist_list.html",{"page_obj":page_obj})

@user_passes_test(is_manager, login_url='login')
def staff_list(request):
    users = User.objects.filter(is_staff=True,is_superuser=False)

    #paginator
    paginator = Paginator(users,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"manager/staff_list.html",{"page_obj":page_obj})

@user_passes_test(is_manager, login_url='login')
def delete_user(request,user_id):
    user = get_object_or_404(User,id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'ลบผู้ใช้งานสำเร็จ')
        return redirect('user-list')
    return redirect('user-list')
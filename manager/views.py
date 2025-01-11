from django.shortcuts import render,get_object_or_404,redirect
from Sparky.models import *
from django.core.paginator import Paginator
from .forms import *
from django.db.models import Q,Count,Sum
from datetime import datetime
from django.db.models.functions import TruncMonth
# Create your views here.
def calculate_age(birth_date):
    today = datetime.now()
    return today.year - birth_date.year - ((today.month,today.day)<(birth_date.month, birth_date.day))

def dashboard(request):
    # ปีปัจจุบัน
    current_year = datetime.now().year
    appointments = Appointment.objects.filter(date__year=current_year,date__isnull=False)

    # คำนวณช่วงอายุ
    age_ranges = [
        (0,18),(19,30),(31,45),(46,60),(61,100)
    ]
    age_range_labels = [
        "0-18", "19-30", "31-45", "46-60", "61+"
    ]
    # นับจำนวนผู้ป่วยตามช่วงอายุ
    patients_by_age = []
    for i,age_range in enumerate(age_ranges):
        count = Profile.objects.filter(
            user__is_superuser=False,
            user__is_manager=False,
            user__is_dentist=False,
            user__is_staff=False,
            birthDate__isnull=False,
            birthDate__lte=datetime.now().replace(year=datetime.now().year - age_range[0]),
            birthDate__gt=datetime.now().replace(year=datetime.now().year - age_range[1] - 1)
        ).count()
        patients_by_age.append({'range': age_range_labels[i], 'total': count})

    patients_by_gender = (
        Profile.objects.filter(
            user__is_superuser=False,
            user__is_manager=False,
            user__is_dentist=False,
            user__is_staff=False)
        .values('gender')
        .annotate(total=Count('id'))
        .order_by('gender')  # เรียงตามเพศ
    )

     # นับจำนวนการนัดหมายตามทันตแพทย์
    dentist_workload = (
        Appointment.objects.filter(date__isnull=False)
        .values('dentist__user__title','dentist__user__first_name', 'dentist__user__last_name')
        .annotate(total_appointments=Count('id'))
        .order_by('-total_appointments')  # เรียงจากทันตแพทย์ที่มีงานมากไปน้อย
    )

    # รายได้รวมตามเดือนในปีปัจจุบัน
    revenue_by_month = (
        TreatmentHistory.objects.filter(appointment__date__year=current_year)
        .annotate(month=TruncMonth('appointment__date'))
        .values('month')
        .annotate(total_revenue=Sum('cost'))
        .order_by('month')
    )

     # รายได้รวมแยกตามประเภทการรักษา
    revenue_by_treatment = (
        TreatmentHistory.objects.values('appointment__treatment__treatmentName')
        .annotate(total_revenue=Sum('cost'))
        .order_by('-total_revenue')
    )

    # การนับจำนวนการนัดหมายตามประเภทการรักษา
    treatment_popularity = (
        Appointment.objects.filter(status="สำเร็จ")
        .values('treatment__treatmentName')
        .annotate(total_appointments=Count('id'))
        .order_by('-total_appointments')  # เรียงตามจำนวนการนัดหมายมากไปน้อย
    )

    appointments_by_status = appointments.values('status').annotate(total=Count('id'))
    appointments_by_month = appointments.annotate(month=TruncMonth('date')).values('month').annotate(total=Count('id')).order_by('month')

     # แมปตัวเลขเดือนเป็นชื่อเดือนภาษาไทย
    month_names = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                   "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    for month in appointments_by_month:
        month_number = month['month'].month
        month['month_name'] = month_names[month_number - 1]

    for month in revenue_by_month:
        month_number = month['month'].month
        month['month_name'] = month_names[month_number - 1]
    return render(request,"manager/dashboard.html",{ 'appointments_by_month': appointments_by_month,
                                                     'appointments_by_status': appointments_by_status,
                                                     'revenue_by_month': revenue_by_month,
                                                     'revenue_by_treatment': revenue_by_treatment,
                                                     'treatment_popularity': treatment_popularity,
                                                     'patients_by_gender': patients_by_gender,
                                                     'patients_by_age': patients_by_age,
                                                     'dentist_workload': dentist_workload,
                                                    })

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

def update_role(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        role = request.POST.get("role")
        user = get_object_or_404(User, id=user_id)
        if role == "Staff":
            user.is_staff = True
            user.is_dentist = False
            user.save()
            return redirect('staff-list')
        elif role == "Dentist":
            user.is_staff = False
            user.is_dentist = True
            user.save()
            return redirect('dentist-list')
        else:  # Member
            user.is_staff = False
            user.is_dentist = False
            user.save()
            return redirect('user-list')

def dentist_list(request):
    users = User.objects.filter(is_dentist=True)

    #paginator
    paginator = Paginator(users,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"manager/dentist_list.html",{"page_obj":page_obj})

def staff_list(request):
    users = User.objects.filter(is_staff=True,is_superuser=False)

    #paginator
    paginator = Paginator(users,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"manager/staff_list.html",{"page_obj":page_obj})

def delete_user(request,user_id):
    user = get_object_or_404(User,id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user-list')
    return redirect('user-list')
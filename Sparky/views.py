from django.shortcuts import render,redirect,get_object_or_404
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout
from django.contrib import messages
from datetime import datetime
from .models import User,Profile
from django.http import HttpResponseForbidden

# Create your views here.
def firstpage(request):
    return render(request,"firstpage.html")

def calculate_age(birth_date):
    if birth_date is None:  # ตรวจสอบว่ามีค่า birth_date หรือไม่
        return ""  # ถ้าไม่มีวันเกิด ให้คืนค่า ""
    
    today = datetime.now().date()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

@login_required(login_url='login')
def showprofile(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # ตรวจสอบว่าเป็นเจ้าของข้อมูล, staff, หรือ dentist
    if request.user.id != user_id and not request.user.is_staff and not request.user.is_dentist:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์เข้าถึงโปรไฟล์นี้")
    
    if hasattr(user, 'profile') and user.profile.birthDate:
        age = calculate_age(user.profile.birthDate)
    else:
        age = ""
    
    return render(request, "sparky/profile.html", {'user': user, 'age': age})  


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']  # ใช้ cleaned_data เพื่อความปลอดภัย
            password = form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)
            if user is not None:
                auth_login(request,user)
                if user.is_staff:
                    messages.success(request,'เข้าสู่ระบบสำเร็จ')
                    return redirect('staff-home')
                elif user.is_manager:
                    messages.success(request,'เข้าสู่ระบบสำเร็จ')
                    return redirect('dashboard')
                elif user.is_dentist:
                    messages.success(request,'เข้าสู่ระบบสำเร็จ')
                    return redirect('dentist-home')
                else:
                    messages.success(request,'เข้าสู่ระบบสำเร็จ')
                    return redirect('member-home')
            else:
                messages.error(request,'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
                return redirect('login')
    return render(request,'registration/login.html')

@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    return redirect('firstpage')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'สมัครสมาชิกสำเร็จ')
            return redirect('profile-form',user_id=user.id)   
        else:
            messages.error(request, 'ข้อมูลไม่ถูกต้อง กรุณาตรวจสอบข้อมูลที่กรอก')
            return redirect('register')
    return render(request,'registration/register.html')

def profile(request,user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST,request.FILES)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'เพิ่มข้อมูลส่วนตัวสำเร็จ')
            return redirect('login')
        else:
            messages.error(request, 'ข้อมูลไม่ถูกต้อง กรุณาตรวจสอบข้อมูลที่กรอก')
            return redirect('profile-form',user_id=user.id)      
    return render(request,'registration/profile_form.html')

@login_required(login_url='login')
def updateprofile(request, user_id):
    if request.user.id != user_id :
        return HttpResponseForbidden("คุณไม่มีสิทธิ์เข้าถึงโปรไฟล์นี้")  
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)  
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'อัปเดตโปรไฟล์สำเร็จแล้ว')
            return redirect('profile', user_id=user.id)
        else:
            messages.error(request, 'ข้อมูลที่กรอกไม่ถูกต้อง')
            return redirect('update-profile', user_id=user.id)
    context = {
        'user': user, 
        'profile': profile
    }
    return render(request, 'sparky/update_profile.html', context)
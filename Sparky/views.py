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
    

    age = calculate_age(user.profile.birthDate)  # คำนวณอายุ
    
    
    return render(request, "sparky/profile.html", {'user': user, 'age': age})  # ส่งค่าอายุไปยังเทมเพลต


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
                    # Redirect ไปหน้า staff
                    return redirect('staff-home')
                elif user.is_manager:
                    # Redirect ไปหน้า manager
                    return redirect('dashboard')
                elif user.is_dentist:
                    # Redirect ไปหน้า dentist
                    return redirect('dentist-home')
                else:
                    # Redirect ไปหน้า member
                    return redirect('member-home')
            else:
                messages.error(request,'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    else:
        form = LoginForm()
    return render(request,'registration/login.html',{'form':form})

@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    return redirect('firstpage')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('profile-form',user_id=user.id)   
        else:
            messages.error(request, 'ข้อมูลไม่ถูกต้อง กรุณาตรวจสอบข้อมูลที่กรอก')
    else:
        form = RegisterForm()

    # ล้าง messages หลังจากแสดงผล
    storage = messages.get_messages(request)
    list(storage)  # ดึงข้อความทั้งหมดเพื่อบังคับให้ระบบล้าง

    return render(request,'registration/register.html',{'form':form})

def profile(request,user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST,request.FILES)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('login')
              
    else:
        profile_form = ProfileForm()

    return render(request,'registration/profile_form.html',{'profile_form':profile_form})

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

          
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'user': user, 
        'profile': profile
    }
    # ล้าง messages หลังจากแสดงผล
    storage = messages.get_messages(request)
    list(storage)  # ดึงข้อความทั้งหมดเพื่อบังคับให้ระบบล้าง
    return render(request, 'sparky/update_profile.html', context)
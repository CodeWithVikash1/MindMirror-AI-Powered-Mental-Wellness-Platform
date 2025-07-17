import random
from django.shortcuts import render,redirect
from django.core.mail import send_mail
from django.contrib import messages
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.db.models import Count

# Create your views here.

def index(request):
    return render(request,'index.html')

# Generate OTP function
def generate_otp():
    return str(random.randint(100000, 999999))

def signup(request):
    if request.method == 'POST':
        if 'send_otp' in request.POST:
            email = request.POST.get('email')
            otp = generate_otp()
            EmailOTP.objects.update_or_create(email=email,defaults={'otp':otp})
            
            send_mail(
                'Your MindMirror OTP',
                f'Your OTP is: {otp}',
                'gargvv156@gmail.com',
                [email],
                fail_silently=False,
            )
            messages.success(request,f'OTP send to {email}')
            return render(request,'signup.html',{'email':email})
        
        else:
            email = request.POST.get('email')
            otp = request.POST.get('otp')
            fullname = request.POST.get('fullname')
            try:
                record = EmailOTP.objects.get(email=email)
                if record.otp != otp:
                    messages.error(request, "Invalid OTP")
                    return render(request,'signup.html',{'email':email,'otp':otp,'fullname':fullname}) 
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')
                
                if password1 != password2:
                    messages.error(request, "Passwords does not match")
                    return render(request,'signup.html',{'email':email,'otp':otp,'fullname':fullname})

                
                if User.objects.filter(email=email).exists():
                    messages.warning(request, "Email already registered please login.")
                    return redirect('signup')
                User.objects.create_user(username=email, email=email,first_name=fullname, password=password1)
                record.delete()
                messages.success(request, "Account created successfully. Please login.")
                return redirect('login')
            except EmailOTP.DoesNotExist:
                messages.error(request, "Please send OTP first")
                return redirect('signup')
    return render(request,'signup.html')
                
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(username=email, password=password)
        
        if user is not None:
            login(request,user)
            messages.success(request,'Login Successful.')
            return redirect('user_home')
        else:
            messages.error(request, "Invalid email or password.")
    return render(request,'login.html')

def user_home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request,'user_home.html')

def Logout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    logout(request)
    return redirect('index')

def track_mood(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        user = request.user
        mood = request.POST.get('mood')
        note = request.POST.get('note')
        
        MoodEntry.objects.create(user=user,mood=mood,note=note)
        messages.success(request, "Your mood has been tracked successfully.")
        return redirect('track_mood')
    return render(request,'track_mood.html')

def my_reflections(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        Reflection.objects.create(user=user,title=title,content=content)
        messages.success(request, "Reflection saved successfully.")
        return redirect('my_reflections')
    
    reflections = Reflection.objects.filter(user=user).order_by('-date')
    return render(request,'my_reflections.html',{'reflections':reflections})

def view_reflection(request,id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    reflection = Reflection.objects.get(id=id,user=user)
    return render(request,'view_reflection.html',{'reflection':reflection})

def insights(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    moods = MoodEntry.objects.filter(user=user).order_by('created_at')
    mood_map = {
        "Sad": 1,
        "Angry": 2,
        "Anxious": 3,
        "Calm": 4,
        "Happy": 5,
        "Excited": 6
    }

    mood_dates = [entry.created_at.strftime("%d %b") for entry in moods]
    mood_scores = [mood_map.get(entry.mood, 0) for entry in moods]

    mood_count = moods.values('mood').annotate(count=Count('mood')).order_by('-count')
    most_common_mood = mood_count[0]['mood'] if mood_count else None

    context = {
        'most_common_mood': most_common_mood,
        'total_entries': moods.count(),
        'active_days': moods.values('created_at__date').distinct().count(),
        'mood_dates': mood_dates,
        'mood_scores': mood_scores,
    }
    return render(request,'insights.html',{'context':context})

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request,'profile.html')


def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        if fullname:
            name_parts = fullname.strip().split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.save()
            messages.success(request, "Profile updated successfully.")
        return redirect('profile')
    return render(request,'edit_profile.html')
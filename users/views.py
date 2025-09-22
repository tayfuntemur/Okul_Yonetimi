
from .models import CustomUser
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm,CustomUserChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login,logout

@login_required  
def home(request):
    return render(request,'home.html')


        
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Giriş başarılı!")
            return redirect('home')
        else:
            messages.error(request, "Kullanıcı adı veya şifre hatalı.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})
        

@login_required
def update_user_view(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Güncelleme başarılı!")
            return redirect('home')
        else:
            messages.error(request, "Lütfen formu doğru doldurun.")
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'users/update.html', {'form': form})

            
@login_required             
def logout_view(request):
    logout(request)
    messages.info(request, "Oturum kapatıldı.")
    return redirect('users:login_view')
    
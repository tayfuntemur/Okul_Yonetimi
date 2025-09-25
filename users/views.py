from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from users.models import CustomUser  # ← Bunu böyle yap
from typing import cast



@login_required
def change_password_view(request):
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = cast(CustomUser, form.save())  # ← Tip belirttik
            user.password_changed = True
            user.save()
            
            # Oturumu güncelle
            update_session_auth_hash(request, user)
            
            messages.success(request, "Şifreniz başarıyla değiştirildi!")
            return redirect('home')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})

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
def logout_view(request):
    logout(request)
    messages.info(request, "Oturum kapatıldı.")
    return redirect('users:login_view')
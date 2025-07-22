from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Devamsizlik

@login_required
def ogrenci_devamsizlik(request):
    # Sadece öğrenci giriş yaptıysa devam
    user = request.user
    if not hasattr(user, 'ogrenci'):
        return redirect('users:home')

    ogrenci = user.ogrenci
    devamsizliklar = Devamsizlik.objects.filter(ogrenci=ogrenci)

    context = {
        'ogrenci': ogrenci,
        'devamsizliklar': devamsizliklar
    }
    return render(request, 'devamsizlik/ogrenci_devamsizlik.html', context)

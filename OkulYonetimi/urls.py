
from django.contrib import admin
from django.urls import path,include
from users.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'), 
    path('users/', include('users.urls')),
    path('devamsizlik/', include('devamsizlik.urls')),
    path('not_gir/', include('not_gir.urls')),
]

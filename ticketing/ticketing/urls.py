"""
URL configuration for ticketing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD

    path('departments/', include('departments.urls')),
    path('services/', include('services.urls')),
=======
    path('accounts/', include('accounts.urls')),
    path('', include('departments.urls')),
>>>>>>> counter
    path('tickets/', include('tickets.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # <-- put it here
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/login/'
    ), name='password_reset_confirm'),
    path('accounts/', include('django.contrib.auth.urls')), 
    path('user/', include('user.urls')),
<<<<<<< HEAD

    # Optional: redirect root to accounts page
=======
>>>>>>> f7ab577c541ae732dae46b59b650735189afc0be
    path('', include('accounts.urls')),
]

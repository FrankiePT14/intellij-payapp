"""webapps2024 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

from payapp.views import CurrencyConversion
from register import views as register_views
from payapp import views as payapp_views
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                path('', RedirectView.as_view(url='home/', permanent=True)),
                path('admin/', admin.site.urls),
                path('admin-dashboard/', payapp_views.admin_view, name='admin-dashboard'),
                path('home/', register_views.home, name="home"),
                path('signup/', register_views.signup_user, name="signup"),
                path('signin/', register_views.signin_user, name="signin"),
                path('logout/', register_views.logout_user, name="logout"),
                path('transfer/', payapp_views.currency_transfer, name="transfer"),
                path('request/', payapp_views.currency_request, name="request"),
                path('profile/', payapp_views.profile, name="profile"),
                path('conversion/<str:currency1>/<str:currency2>/<str:amount>/', CurrencyConversion.as_view(),
                    name='currency_conversion'),
                path('transfer_history/', payapp_views.transfer_history, name="transfer_history"),
                path('api/', include('api.urls')),
                path('requests_page/', payapp_views.currency_request_view, name='requests_page'),
                path('admin_transactions/', payapp_views.all_transactions, name='admin_transactions'),
                path('add_admins/', payapp_views.add_admins, name='add_admins'),



              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

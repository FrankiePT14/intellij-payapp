from django.contrib import admin
from django.urls import path, include
from api.views import CurrencyList, CurrencyDetail

urlpatterns = [
    path('currencies/', CurrencyList.as_view(), name="currencies"),
    path('currencies/<int:pk>/', CurrencyDetail.as_view()),

]

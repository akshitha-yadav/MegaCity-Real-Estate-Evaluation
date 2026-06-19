from django.urls import path
from . import views

urlpatterns = [
    path('', views.adminhome, name='adminhome'),
    path('predictions/', views.adminuserpredictions, name='adminuserpredictions'),
    path('toggle/<int:user_id>/', views.admin_update_userstatus, name='admin_update_userstatus'),
]

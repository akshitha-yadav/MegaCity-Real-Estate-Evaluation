from django.urls import path
from . import views

urlpatterns = [
    path('userhome/', views.userhome, name='userhome'),
    path('predict/', views.predict_house_price, name='userpredict'),
    path('logout/', views.logout_view, name='user_logout'),
]

from django.contrib import admin
from django.urls import path, include
from User import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # HOME
    path('', user_views.index, name='home'),
    path('', user_views.index, name='home_page'),  # alias

    # AUTH
    path('login/', user_views.login_view, name='login_page'),
    path('register/', user_views.register, name='register_page'),
    path('logout/', user_views.logout_view, name='logout'),

    # USER FEATURES
    path('user/', include('User.urls')),

    # ADMIN PANEL
    path('admins/', include('Admins.urls')),
]

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('profile/', views.profile, name = "profile"),
    path('register/', views.register, name="register"),

]
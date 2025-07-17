from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('login/',views.login_view,name='login'),
    path('signup/',views.signup,name='signup'),
    path('user_home/',views.user_home,name='user_home'),
    path('logout/',views.Logout,name='logout'),
    path('track_mood/',views.track_mood,name='track_mood'),
    path('my_reflections/',views.my_reflections,name='my_reflections'),
    path('view_reflection/<int:id>/',views.view_reflection,name='view_reflection'),
    path('insights/',views.insights,name='insights'),
    path('profile/',views.profile,name='profile'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),
]

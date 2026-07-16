from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('following/', views.following_page, name='following'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('explore/', views.explore, name='explore'),
    path('friends/', views.friends, name='friends'),
    path('search/users/', views.search_users, name='search_users'),
    path('@<str:username>/', views.user_profile, name='user_profile'),
]

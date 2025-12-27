from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('post-job/', views.post_job, name='post_job'),
    path('', views.job_list, name='job_list'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('job/<int:job_id>/', views.job_details, name='job_details'),
    path('manage-applications/<int:job_id>/', views.manage_applications, name='manage_applications'),
    path('edit-job/<int:job_id>/', views.edit_job, name='edit_job'),
    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),
]

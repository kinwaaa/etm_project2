from django.urls import path
from .views import (
    main_view, register_view, login_view, logout_view, admin_dashboard,
    manager_dashboard, employee_dashboard, client_dashboard, home_redirect,
    add_user, update_user, delete_user, add_project, update_project, delete_project,
    add_task, update_task, delete_task, add_department, update_department, delete_department,
    add_billing, update_billing, delete_billing, employee_dashboard
)

urlpatterns = [
    # Home & Authentication
    path('', main_view, name='main_html'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Dashboards
    path('admin-dashboard/', admin_dashboard, name='admin-dashboard'),
    path('manager/', manager_dashboard, name='manager_dashboard'),
    path('client/', client_dashboard, name='client_dashboard'),

    # Users
    path('add-user/', add_user, name='add-user'),
    path('update-user/<int:user_id>/', update_user, name='update-user'),
    path('delete-user/<int:user_id>/', delete_user, name='delete-user'),

    # Projects
    path('add-project/', add_project, name='add-project'),
    path('update-project/<int:project_id>/', update_project, name='update-project'),
    path('delete-project/<int:project_id>/', delete_project, name='delete-project'),

    # Tasks
    path('dashboard/task/add/', add_task, name='add_task'),
    path('dashboard/task/<int:task_id>/update/', update_task, name='update_task'),
    path('dashboard/task/<int:task_id>/delete/', delete_task, name='delete_task'),
    path('employee/dashboard/', employee_dashboard, name='employee_dashboard'),



    #Department
    path('dashboard/department/add/', add_department, name='add-department'),
    path('dashboard/department/update/<int:department_id>/', update_department, name='update-department'),
    path('dashboard/department/delete/<int:department_id>/', delete_department, name='delete-department'),

    # Billings
    path('dashboard/billing/add/', add_billing, name='add_billing'),
    path('dashboard/billing/<int:billing_id>/update/', update_billing, name='update_billing'),
    path('dashboard/billing/<int:billing_id>/delete/', delete_billing, name='delete_billing'),

]

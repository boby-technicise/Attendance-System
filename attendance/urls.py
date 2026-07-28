from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('mark/', views.MarkAttendanceView.as_view(), name='mark_attendance'),
    path('leave/apply/', views.ApplyLeaveView.as_view(), name='apply_leave'),
    path('leave/manage/', views.ManageLeavesView.as_view(), name='manage_leaves'),
    path('salary/', views.SalaryView.as_view(), name='salary'),
    path('reports/', views.AttendanceReportView.as_view(), name='attendance_report'),
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', views.CreateEmployeeView.as_view(), name='create_employee'),
    path('employees/upload/', views.BulkUploadEmployeeView.as_view(), name='upload_employees'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('employees/<int:user_id>/change-password/', views.AdminChangeUserPasswordView.as_view(), name='admin_change_user_password'),
]


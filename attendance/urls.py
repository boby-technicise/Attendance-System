from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('mark/', views.MarkAttendanceView.as_view(), name='mark_attendance'),
    path('leave/apply/', views.ApplyLeaveView.as_view(), name='apply_leave'),
    path('salary/', views.SalaryView.as_view(), name='salary'),
    path('reports/', views.AttendanceReportView.as_view(), name='attendance_report'),
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
]

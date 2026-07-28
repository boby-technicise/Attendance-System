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
    path('employees/export/', views.ExportEmployeesExcelView.as_view(), name='export_employees'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('employees/<int:user_id>/change-password/', views.AdminChangeUserPasswordView.as_view(), name='admin_change_user_password'),
    path('employees/<int:user_id>/toggle-active/', views.ToggleUserActiveView.as_view(), name='toggle_user_active'),
    path('employees/<int:employee_id>/edit/', views.EditEmployeeView.as_view(), name='edit_employee'),
    path('employees/<int:employee_id>/fnf/', views.FnFSettlementView.as_view(), name='fnf_settlement'),
    path('audit-log/', views.AuditLogView.as_view(), name='audit_log'),
    path('profile/', views.EmployeeProfileView.as_view(), name='employee_profile'),
]


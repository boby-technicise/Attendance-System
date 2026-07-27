from django.contrib import admin
from django.contrib import messages
from .models import Employee, Attendance, LeaveRequest
from .services import approve_leave, reject_leave


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'designation', 'monthly_salary')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'employee_id', 'department')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'time_in', 'time_out')
    list_filter = ('status', 'date')
    search_fields = ('employee__user__username', 'employee__employee_id')
    date_hierarchy = 'date'


def _approve_leaves(modeladmin, request, queryset):
    count = 0
    for leave in queryset.filter(status='PENDING'):
        approve_leave(leave, reviewed_by=request.user)
        count += 1
    modeladmin.message_user(request, f"{count} leave request(s) approved and attendance records created.", messages.SUCCESS)

_approve_leaves.short_description = "✅ Approve selected leave requests"


def _reject_leaves(modeladmin, request, queryset):
    count = 0
    for leave in queryset.filter(status='PENDING'):
        reject_leave(leave, reviewed_by=request.user)
        count += 1
    modeladmin.message_user(request, f"{count} leave request(s) rejected.", messages.WARNING)

_reject_leaves.short_description = "❌ Reject selected leave requests"


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'applied_on', 'reviewed_by')
    list_filter = ('status', 'leave_type')
    search_fields = ('employee__user__username', 'employee__employee_id')
    readonly_fields = ('applied_on',)
    actions = [_approve_leaves, _reject_leaves]

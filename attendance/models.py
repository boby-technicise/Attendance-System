from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100, blank=True, default='General')
    designation = models.CharField(max_length=100, blank=True, default='Staff')
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Extended Onboarding Fields
    date_of_hiring = models.DateField(blank=True, null=True)
    pt_location = models.CharField(max_length=100, blank=True, null=True)
    annual_ctc = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    provident_fund = models.BooleanField(default=False)
    pf_uan = models.CharField(max_length=30, blank=True, null=True)
    esic_number = models.CharField(max_length=30, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Financial/Tax History Fields
    taxable_salary_current_fy = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    exemptions_current_fy = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tds_deducted_current_fy = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    past_taxable_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    past_tds = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    date_of_exit = models.DateField(blank=True, null=True)

    def __str__(self):
        name = self.user.get_full_name()
        if not name:
            name = self.user.username
        return f"{name} ({self.employee_id})"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LEAVE', 'Leave'),
        ('HALF_DAY', 'Half Day'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.user.username} - {self.date} - {self.get_status_display()}"

    @property
    def total_working_hours(self):
        if self.time_in and self.time_out:
            dummy_date = date(2000, 1, 1)
            datetime_in = datetime.combine(dummy_date, self.time_in)
            datetime_out = datetime.combine(dummy_date, self.time_out)
            if datetime_out < datetime_in:
                datetime_out += timedelta(days=1)
            duration = datetime_out - datetime_in
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "--"



class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    LEAVE_TYPE_CHOICES = [
        ('SICK', 'Sick Leave'),
        ('CASUAL', 'Casual Leave'),
        ('EARNED', 'Earned Leave'),
        ('HALF_DAY', 'Half Day'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES, default='CASUAL')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    applied_on = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='reviewed_leaves'
    )

    class Meta:
        ordering = ['-applied_on']

    @property
    def duration_days(self):
        if self.leave_type == 'HALF_DAY':
            return "0.5 day"
        days = (self.end_date - self.start_date).days + 1
        return f"{days} day{'s' if days > 1 else ''}"

    def __str__(self):
        return f"{self.employee} | {self.get_leave_type_display()} | {self.start_date} to {self.end_date} [{self.status}]"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('DEACTIVATE', 'Account Deactivated / Left Company'),
        ('REACTIVATE', 'Account Reactivated'),
        ('EDIT_PROFILE', 'Profile Edited'),
        ('RESET_PASSWORD', 'Password Reset'),
        ('CREATE_EMPLOYEE', 'Employee Created'),
    ]

    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_actions')
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_targets')
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_action_type_display()} on {self.target_user} by {self.actor} at {self.timestamp.strftime('%d/%m/%Y %H:%M')}"


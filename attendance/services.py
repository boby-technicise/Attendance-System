"""
attendance/services.py
Business logic for leave approval and day-wise salary calculation.
"""
import calendar
from datetime import date, timedelta
from decimal import Decimal
from .models import Attendance


def approve_leave(leave_request, reviewed_by=None):
    """
    Approve a LeaveRequest.
    - Marks the request as APPROVED.
    - Auto-creates Attendance records (status=LEAVE) for every calendar day
      in the requested date range.
    """
    leave_request.status = 'APPROVED'
    if reviewed_by:
        leave_request.reviewed_by = reviewed_by
    leave_request.save()

    current = leave_request.start_date
    while current <= leave_request.end_date:
        Attendance.objects.update_or_create(
            employee=leave_request.employee,
            date=current,
            defaults={'status': 'LEAVE'}
        )
        current += timedelta(days=1)


def reject_leave(leave_request, reviewed_by=None):
    """Mark a LeaveRequest as REJECTED."""
    leave_request.status = 'REJECTED'
    if reviewed_by:
        leave_request.reviewed_by = reviewed_by
    leave_request.save()


def calculate_monthly_salary(employee, year, month):
    """
    Calculate an employee's day-wise gross salary for a given month.

    Rules:
    - Daily Wage  = monthly_salary / total_days_in_month
    - Payable Days = PRESENT days + APPROVED LEAVE days + (HALF_DAY × 0.5)
    - Gross Salary = Payable Days × Daily Wage
    """
    _, total_days = calendar.monthrange(year, month)
    monthly_salary = Decimal(str(employee.monthly_salary))

    if monthly_salary <= 0:
        daily_wage = Decimal('0.00')
    else:
        daily_wage = monthly_salary / Decimal(str(total_days))

    records = Attendance.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month
    )

    present_days  = records.filter(status='PRESENT').count()
    leave_days    = records.filter(status='LEAVE').count()
    half_days     = records.filter(status='HALF_DAY').count()
    absent_days   = records.filter(status='ABSENT').count()

    payable_days  = Decimal(str(present_days)) + Decimal(str(leave_days)) + Decimal(str(half_days)) * Decimal('0.5')
    gross_salary  = payable_days * daily_wage

    return {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'total_days': total_days,
        'present_days': present_days,
        'leave_days': leave_days,
        'half_days': half_days,
        'absent_days': absent_days,
        'payable_days': float(payable_days),
        'daily_wage': round(daily_wage, 2),
        'gross_salary': round(gross_salary, 2),
        'monthly_salary': monthly_salary,
    }

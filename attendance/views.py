from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Employee, Attendance, LeaveRequest
from .services import calculate_monthly_salary, approve_leave, reject_leave
from django.contrib import messages
from datetime import datetime, date, timedelta
import calendar


def get_or_create_employee(user):
    employee = Employee.objects.filter(user=user).first()
    if not employee:
        emp_id = f"EMP-{user.id:03d}"
        if Employee.objects.filter(employee_id=emp_id).exists():
            emp_id = f"EMP-U{user.id}"
        employee = Employee.objects.create(
            user=user,
            employee_id=emp_id,
            monthly_salary=50000
        )
    return employee


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = get_or_create_employee(self.request.user)
        return context


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'attendance/employee_list.html'
    context_object_name = 'employees'


class MarkAttendanceView(LoginRequiredMixin, View):
    def get(self, request):
        today = timezone.now().date()

        try:
            year = int(request.GET.get('year', today.year))
            month = int(request.GET.get('month', today.month))
        except ValueError:
            year = today.year
            month = today.month

        if month == 1:
            prev_month, prev_year = 12, year - 1
        else:
            prev_month, prev_year = month - 1, year

        if month == 12:
            next_month, next_year = 1, year + 1
        else:
            next_month, next_year = month + 1, year

        employee = get_or_create_employee(request.user)

        cal = calendar.Calendar(firstweekday=6)  # Sunday first
        month_days = cal.monthdatescalendar(year, month)

        attendance_dict = {}
        if employee:
            for record in Attendance.objects.filter(employee=employee, date__year=year, date__month=month):
                attendance_dict[record.date] = record.status

        calendar_data = []
        for week in month_days:
            week_data = []
            for d in week:
                week_data.append({
                    'date': d,
                    'day': d.day,
                    'is_current_month': d.month == month,
                    'is_today': d == today,
                    'status': attendance_dict.get(d),
                })
            calendar_data.append(week_data)

        has_checked_in = False
        has_checked_out = False
        working_hours = None

        if employee:
            try:
                today_att = Attendance.objects.get(employee=employee, date=today)
                has_checked_in = bool(today_att.time_in)
                if today_att.time_out:
                    has_checked_out = True
                    t_in = datetime.combine(date.min, today_att.time_in)
                    t_out = datetime.combine(date.min, today_att.time_out)
                    working_hours = round((t_out - t_in).total_seconds() / 3600, 2)
            except Attendance.DoesNotExist:
                pass

        leave_requests = LeaveRequest.objects.filter(employee=employee) if employee else []

        context = {
            'today': today,
            'calendar_data': calendar_data,
            'has_checked_in': has_checked_in,
            'has_checked_out': has_checked_out,
            'working_hours': working_hours,
            'employee': employee,
            'month_name': calendar.month_name[month],
            'year': year,
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
            'leave_requests': leave_requests,
        }
        return render(request, 'attendance/mark_attendance.html', context)

    def post(self, request):
        today = timezone.now().date()
        action = request.POST.get('action')

        employee = get_or_create_employee(request.user)

        if action == 'checkin':
            Attendance.objects.update_or_create(
                employee=employee, date=today,
                defaults={'status': 'PRESENT', 'time_in': timezone.now().time()}
            )
            messages.success(request, 'Successfully checked in for today!')

        elif action == 'checkout':
            attendance = Attendance.objects.filter(employee=employee, date=today).first()
            if attendance and not attendance.time_out:
                attendance.time_out = timezone.now().time()
                attendance.save()
                messages.success(request, 'Successfully checked out. Have a good day!')

        return redirect('mark_attendance')


class ApplyLeaveView(LoginRequiredMixin, View):
    def get(self, request):
        employee = get_or_create_employee(request.user)

        leave_requests = LeaveRequest.objects.filter(employee=employee) if employee else []
        context = {
            'employee': employee,
            'leave_type_choices': LeaveRequest.LEAVE_TYPE_CHOICES,
            'leave_requests': leave_requests,
        }
        return render(request, 'attendance/apply_leave.html', context)

    def post(self, request):
        employee = get_or_create_employee(request.user)

        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        leave_type = request.POST.get('leave_type')
        reason = request.POST.get('reason', '').strip()

        if not (start_date_str and end_date_str and leave_type and reason):
            messages.error(request, 'All fields are required.')
            return redirect('apply_leave')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return redirect('apply_leave')

        if end_date < start_date:
            messages.error(request, 'End date cannot be before start date.')
            return redirect('apply_leave')

        LeaveRequest.objects.create(
            employee=employee,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            reason=reason,
        )
        messages.success(request, 'Leave request submitted successfully! Pending admin approval.')
        return redirect('apply_leave')


class SalaryView(LoginRequiredMixin, View):
    def get(self, request):
        today = timezone.now().date()

        try:
            year = int(request.GET.get('year', today.year))
            month = int(request.GET.get('month', today.month))
        except ValueError:
            year, month = today.year, today.month

        if month == 1:
            prev_month, prev_year = 12, year - 1
        else:
            prev_month, prev_year = month - 1, year

        if month == 12:
            next_month, next_year = 1, year + 1
        else:
            next_month, next_year = month + 1, year

        employee = get_or_create_employee(request.user)

        salary_data = None
        monthly_records = []
        if employee:
            salary_data = calculate_monthly_salary(employee, year, month)
            monthly_records = list(
                Attendance.objects.filter(employee=employee, date__year=year, date__month=month)
                .order_by('date')
            )

        context = {
            'today': today,
            'employee': employee,
            'salary_data': salary_data,
            'monthly_records': monthly_records,
            'year': year,
            'month': month,
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
        }
        return render(request, 'attendance/salary.html', context)


class AttendanceReportView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendance/reports.html'
    context_object_name = 'attendance_records'

    def get_queryset(self):
        queryset = super().get_queryset()
        month = self.request.GET.get('month')
        employee_id = self.request.GET.get('employee')
        if month:
            year, m = month.split('-')
            queryset = queryset.filter(date__year=year, date__month=m)
        if employee_id:
            queryset = queryset.filter(employee__id=employee_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        context['selected_month'] = self.request.GET.get('month', '')
        context['selected_employee'] = self.request.GET.get('employee', '')
        return context


class ManageLeavesView(LoginRequiredMixin, View):
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')

        status_filter = request.GET.get('status', 'ALL')
        
        queryset = LeaveRequest.objects.select_related('employee', 'employee__user').all()
        
        pending_count = queryset.filter(status='PENDING').count()
        approved_count = queryset.filter(status='APPROVED').count()
        rejected_count = queryset.filter(status='REJECTED').count()
        total_count = queryset.count()

        if status_filter != 'ALL':
            leave_requests = queryset.filter(status=status_filter)
        else:
            leave_requests = queryset

        context = {
            'leave_requests': leave_requests,
            'status_filter': status_filter,
            'pending_count': pending_count,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'total_count': total_count,
        }
        return render(request, 'attendance/manage_leaves.html', context)

    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')

        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')

        try:
            leave_request = LeaveRequest.objects.get(id=leave_id)
            if action == 'approve':
                approve_leave(leave_request, reviewed_by=request.user)
                messages.success(request, f'Leave for {leave_request.employee} approved successfully! Attendance updated.')
            elif action == 'reject':
                reject_leave(leave_request, reviewed_by=request.user)
                messages.warning(request, f'Leave for {leave_request.employee} has been rejected.')
        except LeaveRequest.DoesNotExist:
            messages.error(request, 'Leave request not found.')

        status_filter = request.POST.get('status_filter', 'ALL')
        return redirect(f"/leave/manage/?status={status_filter}")


class CreateEmployeeView(LoginRequiredMixin, View):
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')
        return render(request, 'attendance/create_employee.html')

    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        department = request.POST.get('department', 'General').strip()
        designation = request.POST.get('designation', 'Staff').strip()
        monthly_salary_str = request.POST.get('monthly_salary', '30000').strip()

        if not (first_name and email and password):
            messages.error(request, 'First name, email, and password are required.')
            return render(request, 'attendance/create_employee.html', {'request_data': request.POST})

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, f'A user with email/username "{email}" already exists.')
            return render(request, 'attendance/create_employee.html', {'request_data': request.POST})

        try:
            monthly_salary = float(monthly_salary_str) if monthly_salary_str else 30000.00
        except ValueError:
            monthly_salary = 30000.00

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        next_id = User.objects.count()
        emp_id = f"EMP-{next_id:03d}"
        while Employee.objects.filter(employee_id=emp_id).exists():
            next_id += 1
            emp_id = f"EMP-{next_id:03d}"

        Employee.objects.create(
            user=user,
            employee_id=emp_id,
            department=department if department else 'General',
            designation=designation if designation else 'Staff',
            phone_number=phone_number,
            address=address,
            monthly_salary=monthly_salary
        )

        messages.success(request, f'Employee account for {first_name} {last_name} ({email}) created successfully! ID: {emp_id}')
        return redirect('create_employee')



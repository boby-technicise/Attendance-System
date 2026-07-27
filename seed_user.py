import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import Employee

try:
    user = User.objects.get(username='testadmin')
    print("User testadmin already exists.")
except User.DoesNotExist:
    user = User.objects.create_superuser('testadmin', 'admin@example.com', 'testpass123')
    user.first_name = "Test"
    user.last_name = "Admin"
    user.save()
    print("Superuser created successfully.")

try:
    emp = Employee.objects.get(user=user)
    print("Employee profile already exists.")
except Employee.DoesNotExist:
    emp = Employee.objects.create(
        user=user,
        employee_id="EMP-001",
        department="Engineering",
        designation="Software Engineer"
    )
    print("Employee profile created successfully.")

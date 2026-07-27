import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from attendance.models import Attendance

today = timezone.now().date()
deleted, _ = Attendance.objects.filter(date=today).delete()
print(f"Deleted {deleted} attendance records for {today}.")

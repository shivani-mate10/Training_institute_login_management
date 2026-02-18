from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from class_management.models import Enrollments

User = get_user_model()

class Command(BaseCommand):
    help = 'Archive students not enrolled in any batch'

    def handle(self, *args, **options):
        students = User.objects.filter(role='student', is_archived=False)
        
        students_with_enrollments = Enrollments.objects.values_list('student_id', flat=True)
        students_to_archive = students.exclude(id__in=students_with_enrollments)
    
        count = students_to_archive.count()
        
        students_to_archive.update(is_archived=True)
        
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully archived {count} students with no batches')
        )
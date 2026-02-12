from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# class User(AbstractUser):

#     ROLE_CHOICES = (
#         ('admin', 'Admin'),
#         ('teacher', 'Teacher'),
#         ('student', 'Student'),
#     )

#     role = models.CharField(max_length=20, choices=ROLE_CHOICES)
#     is_archived=models.BooleanField(default=False)
#     subjects = models.ManyToManyField(Subjects, blank=True)
    


#     def __str__(self):
#         return self.username

    
class Subjects(models.Model):
    
    subject_name=models.CharField(max_length=100 , unique=True)
    is_archive=models.BooleanField(default=False)

    class Meta:
        db_table = 'subjects'


    def __str__(self):
        return self.subject_name
    
class Courses(models.Model):
    course_name=models.CharField(max_length=100,unique=True)
    is_archived=models.BooleanField(default=False)
    subjects = models.ManyToManyField(Subjects, blank=True)
    
    class Meta:
        db_table='courses'
    
    def __str__(self):
        return self.course_name
    
class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_archived=models.BooleanField(default=False)
    subjects = models.ManyToManyField(Subjects, blank=True)
    


    def __str__(self):
        return self.username
    
class Batches(models.Model):
    batch_name=models.CharField(max_length=100, unique=True)
    is_archived=models.BooleanField(default=False)
    start_date=models.DateField(null=True, blank=True)
    duration=models.CharField(max_length=100)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='batches')
    
    
    class Meta:
        db_table='batches'

    def __str__(self):
        return self.Batch_name


class Subject_teacher(models.Model):
    batch=models.ForeignKey(Batches,on_delete=models.CASCADE,related_name="subject_teachers")
    subject=models.ForeignKey(Subjects, on_delete=models.CASCADE,related_name="batch_subjects")
    user=models.ForeignKey(User, on_delete=models.CASCADE,related_name="teacher_subjects")

    class Meta:
        db_table='subject_teacher'

    def __str__(self):
        return f"{self.batch.batch_name} - {self.subject.subject_name} - {self.teacher.teacher_name}"
    

        

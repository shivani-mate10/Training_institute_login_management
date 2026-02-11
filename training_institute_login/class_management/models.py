from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_archived=models.BooleanField(default=False)


    def __str__(self):
        return self.username

    
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

        

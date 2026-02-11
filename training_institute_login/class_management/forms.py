from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User,Subjects,Courses


class Registerform(UserCreationForm):

    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'role', 'password1', 'password2']



class subjectform(forms.ModelForm):
    class Meta:
        model=Subjects
        exclude = ['is_archive']

class courseform(forms.ModelForm):
    class Meta:
        model=Courses
        exclude = ['is_archived']






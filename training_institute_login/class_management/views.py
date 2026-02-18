from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import Registerform ,subjectform,courseform
from django.contrib.auth.decorators import login_required
from .models import User,Subjects,Courses,Marks,Enrollments, Batches,Subject_teacher
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import logout
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import io
from datetime import datetime
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
import json
import requests
import csv
from django.contrib.auth.hashers import make_password


def index(request):
    api_request=requests.get("https://restcountries.com/v3.1/all?fields=name,cca2")
    try:
        api=json.loads(api_request.content)
    except Exception as e:
        api="error, data not loading"
    return render(request,'index.html',{'api':api})


@login_required
def register_user(request):

    if request.method == "POST":
        form = Registerform(request.POST)

        if form.is_valid():
            form.save()
            return redirect("dashboard")  

    else:
        form = Registerform()

    return render(request, "register.html", {"form": form})


def login_user(request):

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")


    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


def logout_user(request):
    logout(request)
    return redirect("login")


# def dashboard_view(request):
#     total_admins = User.objects.filter(role='admin', is_archived=False).count()
#     total_teachers = User.objects.filter(role='teacher', is_archived=False).count()
#     total_students = User.objects.filter(role='student', is_archived=False).count()
#     total_subjects = Subjects.objects.filter(is_archive=False).count()
#     total_courses = Courses.objects.filter(is_archived=False).count()
#     total_batches = Batches.objects.filter(is_archived=False).count()
    
#     context = {
#         'total_admins': total_admins,
#         'total_teachers': total_teachers,
#         'total_students': total_students,
#         'total_subjects': total_subjects,
#         'total_courses': total_courses,
#         'total_batches': total_batches,
#     }
    
#     return render(request, 'dashboard.html', context)


from django.db.models import Count

def dashboard_view(request):
    
    total_admins = User.objects.filter(role='admin', is_archived=False).count()
    total_teachers = User.objects.filter(role='teacher', is_archived=False).count()
    total_students = User.objects.filter(role='student', is_archived=False).count()
    total_subjects = Subjects.objects.filter(is_archive=False).count()
    total_courses = Courses.objects.filter(is_archived=False).count()
    total_batches = Batches.objects.filter(is_archived=False).count()
    
    
    courses = Courses.objects.filter(is_archived=False)
    course_data = []
    
    for course in courses:
        
        batches = Batches.objects.filter(course=course, is_archived=False)
        batch_count = batches.count()
        
        
        student_count = Enrollments.objects.filter(
            batch__course=course,  
            is_archived=False,
            student__is_archived=False 
        ).values('student').distinct().count()  
        
        course_data.append({
            'course_name': course.course_name,
            'batch_count': batch_count,
            'student_count': student_count,
        })
    
    context = {
        'total_admins': total_admins,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_subjects': total_subjects,
        'total_courses': total_courses,
        'total_batches': total_batches,
        'course_data': course_data,
    }
    
    return render(request, 'dashboard.html', context)

# @login_required
# def user_management(request):
#     if request.user.role == "admin":
#         roles = User.ROLE_CHOICES

#     elif request.user.role == "teacher":
#         roles = [
#             ("teacher", "Teacher"),
#             ("student", "Student"),
#         ]

#     elif request.user.role == "student":
#         roles = [
#             ("teacher", "Teacher"),
#             ("student", "Student"),
#         ]  
#     return render(request, "user_management.html", {"roles": roles})
   
def get_countries(request):
    api_request = requests.get("https://restcountries.com/v3.1/all?fields=name")

    countries = []

    if api_request.status_code == 200:
        data = api_request.json()

        for country in data:
            countries.append(country["name"]["common"])

    
    countries.sort()

    return JsonResponse({"countries": countries}) 


@login_required
def user_management(request):

    
    if request.user.role == "admin":
        roles = User.ROLE_CHOICES

    
    else:
        roles = [
            ("teacher", "Teacher"),
            ("student", "Student"),
        ]

    # try:
    #     api_request = requests.get("https://restcountries.com/v3.1/all?fields=name,cca2")
    #     api_data = json.loads(api_request.content)
    #     countries = [country['name']['common'] for country in api_data]
    #     countries.sort()
    # except Exception as e:
    #     countries = []


    return render(request, "user_management.html", {"roles": roles})

# @login_required
# def users_list(request):
    
#     users = User.objects.filter(is_archived=False)
    
    
#     role_filter = request.GET.get('role')
#     if role_filter:
#         users = users.filter(role=role_filter)
    
    
#     users = users.values("id", "first_name", "last_name", "role")

    
#     return JsonResponse({"data": list(users)})

# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from .models import User, Subject_teacher, Enrollments


@login_required
def users_list(request):

    
    users = User.objects.filter(is_archived=False)

    
    role_filter = request.GET.get('role')
    if request.user.role == "student":


        # users = User.objects.filter(
        #     id=request.user.id,
        #     is_archived=False
        # )
        student_batches = Enrollments.objects.filter(
            student=request.user,
            is_archived=False
        ).values_list("batch_id", flat=True)

        
        student_teachers = Subject_teacher.objects.filter(
            batch_id__in=student_batches
        ).values_list("teacher_id", flat=True)

        if role_filter == "student":

            
            users = User.objects.filter(
                id=request.user.id,
                is_archived=False
            )

        elif role_filter == "teacher":

            
            users = User.objects.filter(
                id__in=student_teachers,
                role="teacher",
                is_archived=False
            )

        else:
            
            users = User.objects.filter(
                id=request.user.id,
                is_archived=False
            ) | User.objects.filter(
                id__in=student_teachers,
                role="teacher",
                is_archived=False
            )

        users = users.distinct()

       
        # users = User.objects.filter(
        #     id=request.user.id,
        #     is_archived=False
        # ) | User.objects.filter(
        #     id__in=student_teachers,
        #     role="teacher",
        #     is_archived=False
        # )

       

    
    elif request.user.role == "teacher":

        
        teacher_batches = Subject_teacher.objects.filter(
            teacher=request.user
        ).values_list("batch_id", flat=True)

        
        teacher_students = Enrollments.objects.filter(
            batch_id__in=teacher_batches,
            is_archived=False
        ).values_list("student_id", flat=True)

        
        users = User.objects.filter(
            is_archived=False
        ).filter(
            role="teacher"
        ) | User.objects.filter(
            id__in=teacher_students,
            role="student"
        )

        if role_filter == "teacher":
            
            users = User.objects.filter(
                role="teacher",
                is_archived=False
            )

        elif role_filter == "student":
            
            users = User.objects.filter(
                id__in=teacher_students,
                role="student",
                is_archived=False
            )

        else:
            
            users = User.objects.filter(
                role="teacher",
                is_archived=False
            ) | User.objects.filter(
                id__in=teacher_students,
                role="student",
                is_archived=False
            )


       
        users = users.distinct()

    else:
        
        if role_filter:
            users = users.filter(role=role_filter)

    
    users = users.values("id", "first_name", "last_name", "role","nationality")

    return JsonResponse({"data": list(users)})



# @login_required
# def add_user_ajax(request):
#     if request.method == "POST":
#         form = Registerform(request.POST)

#         if form.is_valid():
#             form.save()
#             return JsonResponse({"success": True})

#         else:
#             return JsonResponse({
#                 "success": False,
#                 "errors": form.errors
#             })

#     return JsonResponse({"success": False, "error": "Invalid request"})

@login_required
def add_user(request):
    print("Add user AJAX called")  
    
    if request.method == "POST":
        print("POST data:", request.POST)  
        
        
        form = Registerform(request.POST)
        print("Form is valid?", form.is_valid())  
        
        if form.is_valid():
            print("Saving user...") 
            form.save()
            print("User saved successfully")  
            return JsonResponse({"success": True})
        else:
            print("Form errors:", form.errors)  
            return JsonResponse({
                "success": False,
                "errors": str(form.errors)  
            })
    
    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required
def delete_user(request, id):
    if request.user.role != "admin":
        return JsonResponse({
            "success": False,
            "message": "You are not allowed to delete users."
        })
    if request.method == "POST":
        try:
            user = User.objects.get(id=id)
            user.is_archived = True
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'User deleted successfully'
            })
            
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


@login_required
def update_user(request, id):

    user = get_object_or_404(User, id=id)
    
    if request.method == "POST":
        try:
           
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.role = request.POST.get('role', user.role)
            user.nationality = request.POST.get('nationality',user.nationality)
            
            user.save()

            if user.role == "teacher":
                subject_ids = request.POST.getlist("subjects")
                user.subjects.set(subject_ids)
            else:
                user.subjects.clear()
            
            return JsonResponse({
                'success': True,
                'message': 'User updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }, status=500)
    
    elif request.method == "GET":
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': user.role,
                'nationality':user.nationality,

                "subjects": list(user.subjects.values_list("id", flat=True))
                
            }
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

#####################################################Subjects###########################################################################



def subject_list(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        subjects = Subjects.objects.filter(is_archive=False)
        
        data = []
        for subject in subjects:
            data.append({
                'id': subject.id,
                'subject_name': subject.subject_name,
            })
        
        return JsonResponse({'data': data})
    
    
    return render(request, 'subject_list.html')

def add_subject(request):
    if request.method=='POST':
        subject_name = request.POST.get('subject_name') 

        subject = Subjects.objects.create(subject_name=subject_name)
        subject.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success":True})
    return redirect('subject_list')

def delete_subject(request, id):
    if request.method == "POST":
        subject= get_object_or_404(Subjects, id=id)
        subject.is_archive = True
        subject.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": True})


    return redirect('subject_list')


def update_subject(request, id):
    subject = get_object_or_404(Subjects, id=id)
    
    if request.method == "POST":

        try:
            
            subject_name = request.POST.get('subject_name')
            if subject_name:
                subject.subject_name = subject_name
            
    
            subject.save()
            
            return JsonResponse({
                'success': True,
                
                'message': 'Subject updated successfully',
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }, status=500)
    
    elif request.method == "GET":
        
        return JsonResponse({
            'success': True,
            'subject': {
                'id': subject.id,
                'subject_name': subject.subject_name,
                
            }
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


            

#######################################################Courses#########################################################



def course_list(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        courses = Courses.objects.filter(is_archived=False).prefetch_related('subjects')
        
        search = request.GET.get('search', '')
        if search:
            courses = courses.filter(course_name__icontains=search)
        
        subject_id = request.GET.get('subject')
        if subject_id:
            courses = courses.filter(subjects__id=subject_id)
        
        data = []
        for course in courses:
            data.append({
                'id': course.id,
                'course_name': course.course_name,
                'subjects': ', '.join([s.subject_name for s in course.subjects.all()]),
                'actions': f'<button class="btn btn-warning btn-sm">Edit</button>'
            })
        
        return JsonResponse({'data': data})
    
    
    subjects = Subjects.objects.filter(is_archive=False)
    return render(request, 'course_list.html', {'subjects': subjects})


def add_course(request):
    if request.method=='POST':
        course_name = request.POST.get('course_name')
        subject_ids = request.POST.getlist('subjects[]') 

        course = Courses.objects.create(course_name=course_name)
        course.subjects.set(subject_ids) 
        course.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success":True})
    return redirect('course_list')


def delete_course(request, id):
    if request.method == "POST":
        course= get_object_or_404(Courses, id=id)
        course.is_archived = True
        course.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": True})


    return redirect('course_list')

def update_course(request, id):
    course = get_object_or_404(Courses, id=id)
    
    if request.method == "POST":
        print("POST data received:", request.POST)  
        print("Subjects received:", request.POST.getlist('subjects[]'))
        try:
            
            course_name = request.POST.get('course_name')
            if course_name:
                course.course_name = course_name
            
           
            subject_ids = request.POST.getlist('subjects[]')
            if subject_ids:
                subjects = Subjects.objects.filter(id__in=subject_ids)
                course.subjects.set(subjects)
            
            course.save()
            
            return JsonResponse({
                'success': True,
                
                'message': 'Course updated successfully',
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }, status=500)
    
    elif request.method == "GET":
        
        return JsonResponse({
            'success': True,
            'course': {
                'id': course.id,
                'course_name': course.course_name,
                'subjects': list(course.subjects.values_list('id', flat=True))
            }
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


#############################################
def subject_list_ajax(request):
    subjects = Subjects.objects.filter(is_archive=False).values("id", "subject_name")
    return JsonResponse({"subjects": list(subjects)})
###################################Batches################################################################
def batch_list(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        batches = Batches.objects.filter(is_archived=False)
         
        if request.user.role == "student":
            enrolled_batches = Enrollments.objects.filter(
                student=request.user,
                is_archived=False
            ).values_list("batch_id", flat=True)

            batches = batches.filter(id__in=enrolled_batches)

        elif request.user.role == "teacher":
            teacher_batches = Subject_teacher.objects.filter(
                teacher=request.user
            ).values_list("batch_id", flat=True)
            batches = batches.filter(id__in=teacher_batches)
        

        course_id = request.GET.get('course')



        if course_id:
            batches = batches.filter(course_id=course_id)

         
        
        data = []
        for batch in batches:
            data.append({
                'id': batch.id,
                'batch_name': batch.batch_name,
                'start_date':batch.start_date,
                'duration':batch.duration,
                'course':batch.course.course_name
            })
        
        return JsonResponse({'data': data})
    
    
    
    courses = Courses.objects.filter(is_archived=False)  
    print(f"Total courses with is_archived=False: {courses.count()}")  
    print("Course names:", [c.course_name for c in courses]) 
    return render(request, 'batch_list.html', {'courses': courses})




def add_batch(request):
    if request.method == 'POST':
        try:
            batch_name = request.POST.get('batch_name')
            start_date = request.POST.get("start_date")
            duration = request.POST.get("duration")
            course_id = request.POST.get("course")

            if not all([batch_name, start_date, duration, course_id]):
                return JsonResponse({
                    "status": "error",
                    "message": "All fields are required!"
                })

            course = Courses.objects.get(id=course_id)

            batch = Batches.objects.create(
                batch_name=batch_name,
                course=course,
                start_date=start_date,
                duration=duration
            )

            subjects = course.subjects.all()
            mapping_count = 0

            for subject in subjects:
                teacher_field_name = f"teacher_{subject.id}"
                teacher_id = request.POST.get(teacher_field_name)

                if teacher_id:
                    try:
                       
                        teacher = User.objects.get(id=teacher_id, role="teacher")

                        Subject_teacher.objects.update_or_create(
                            batch=batch,
                            subject=subject,
                            defaults={'teacher':teacher}
                        )
                        mapping_count += 1

                    except User.DoesNotExist:
                        pass
                else:
                    Subject_teacher.objects.filter(
                        batch=batch,
                        subject=subject
                    ).delete()

            
            return JsonResponse({
                "status": "success",
                "message": f"Batch Updated successfully with {mapping_count} mappings!"
            })

            

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            })


    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    })




def delete_batch(request, id):
    if request.method == "POST":
        batch= get_object_or_404(Batches, id=id)
        batch.is_archived = True
        batch.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": True})


    return redirect('batch_list')



# def update_batch(request, id):
#     batch = get_object_or_404(Batches, id=id)

#     if request.method == "POST":
#         try:
#             batch.batch_name = request.POST.get("batch_name")
#             batch.start_date = request.POST.get("start_date")
#             batch.duration = request.POST.get("duration")

#             course_id = request.POST.get("course")
#             batch.course = get_object_or_404(Courses, id=course_id)
#             batch.save()

            
#             course = batch.course
#             subjects = course.subjects.all()
            
#             mapping_count = 0
#             for subject in subjects:
#                 teacher_field_name = f"teacher_{subject.id}"
#                 teacher_id = request.POST.get(teacher_field_name)
                
#                 if teacher_id:
#                     try:
#                         teacher = User.objects.get(id=teacher_id, role="teacher")
                        
                        
#                         Subject_teacher.objects.update_or_create(
#                             batch=batch,
#                             subject=subject,
#                             defaults={'teacher': teacher}
#                         )
#                         mapping_count += 1
                        
#                     except User.DoesNotExist:
#                         pass
#                 else:
                   
#                     Subject_teacher.objects.filter(
#                         batch=batch,
#                         subject=subject
#                     ).delete()

#             return JsonResponse({
#                 "status": "success",
#                 "message": f"Batch updated successfully with {mapping_count} subject-teacher mappings!"
#             })

#         except Exception as e:
#             return JsonResponse({
#                 "status": "error",
#                 "message": f"An error occurred: {str(e)}"
#             })

#     return JsonResponse({
#         "status": "error",
#         "message": "Invalid request"
#     })



def update_batch(request, id):

    batch = get_object_or_404(Batches, id=id)

    
    if request.method == "GET":
        return JsonResponse({
            "success": True,
            "batch": {
                "id": batch.id,
                "batch_name": batch.batch_name,
                "start_date": batch.start_date.strftime("%Y-%m-%d"),
                "duration": batch.duration,
                "course_id": batch.course.id,
                "course_name": batch.course.course_name  # Add this to the batch dict
                
            }
        })

    
    if request.method == "POST":
        try:
            batch.batch_name = request.POST.get("batch_name")
            batch.start_date = request.POST.get("start_date")
            batch.duration = request.POST.get("duration")
            batch.save()

            course = batch.course
            subjects = course.subjects.all()

            mapping_count = 0

            for subject in subjects:

                teacher_field = f"teacher_{subject.id}"
                teacher_id = request.POST.get(teacher_field)

                if teacher_id:
                    teacher = User.objects.get(
                        id=teacher_id,
                        role="teacher"   
                    )

                    Subject_teacher.objects.update_or_create(
                        batch=batch,
                        subject=subject,
                        defaults={"teacher": teacher}
                    )

                    mapping_count += 1

                else:
                    Subject_teacher.objects.filter(
                        batch=batch,
                        subject=subject
                    ).delete()

            return JsonResponse({
                "status": "success",
                "message": f"Batch updated with {mapping_count} mappings!"
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })

    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    })




def subject_teacher_list(request):

    
    print("FULL GET DATA:", request.GET)

    course_id = request.GET.get("course_id")
    batch_id = request.GET.get("batch_id")

    print("COURSE ID RECEIVED:", course_id)

    course = Courses.objects.get(id=course_id)

    subjects_data = []

    for sub in course.subjects.all():

        
        teachers = User.objects.filter(
            role="teacher",
            subjects=sub
        )

        
        selected_teacher_id = None

        if batch_id:
            mapping = Subject_teacher.objects.filter(
                batch_id=batch_id,
                subject=sub
            ).first()

            if mapping:
                selected_teacher_id = mapping.teacher.id

        subjects_data.append({
            "id": sub.id,
            "name": sub.subject_name,
            "selected_teacher": selected_teacher_id,
            "teachers": [
                {
                    "id": t.id,
                    "name": f"{t.first_name} {t.last_name}"
                }
                for t in teachers
            ]
        })

    return JsonResponse({"subjects": subjects_data})
#####################################Enrollment#####################

def enrollment_list(request):
    students = User.objects.filter(role='student', is_archived=False)
    batches=Batches.objects.filter(is_archived=False)
    enrollments = Enrollments.objects.filter(is_archived=False,student__role='student')
    batch_id = request.GET.get('batch')
    if batch_id:
           enrollments = enrollments.filter(batch_id=batch_id)


        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
       
       
    
        data = []
        for enrollment in enrollments:
            data.append({
                'id': enrollment.id,
                'student_name': enrollment.student.get_full_name() or enrollment.student.username,
                'batch_name': enrollment.batch.batch_name, 
                'start_date': enrollment.batch.start_date.strftime("%Y-%m-%d") if enrollment.batch.start_date else "", 
            })
        
        return JsonResponse({'data': data})
    return render(request, 'enrollment_list.html',{'students': students,'batches': batches})





def add_enrollment(request):
    if request.method == "POST":
        try:
            student_id = request.POST.get("student")
            batch_id = request.POST.get("batch")
            
           
            if not student_id or not batch_id:
                return JsonResponse({
                    "status": "error",
                    "message": "Student and Batch are required"
                })
            
            
            try:
                student = User.objects.get(id=student_id, role='student', is_archived=False)
            except User.DoesNotExist:
                return JsonResponse({
                    "status": "error",
                    "message": "Invalid student selected"
                })
            
            
            try:
                batch = Batches.objects.get(id=batch_id, is_archived=False)
            except Batches.DoesNotExist:
                return JsonResponse({
                    "status": "error",
                    "message": "Invalid batch selected"
                })
            
           
            if Enrollments.objects.filter(student=student, batch=batch, is_archived=False).exists():
                return JsonResponse({
                    "status": "error",
                    "message": "Student is already enrolled in this batch"
                })
            
            
            enrollment = Enrollments.objects.create(
                student=student,
                batch=batch,
                is_archived=False
            )
            
            return JsonResponse({
                "status": "success",
                "message": "Student enrolled successfully!",
                "enrollment_id": enrollment.id
            })
            
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })
    
    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    })



def delete_enrollment(request, id):
    if request.method == "POST":
        enrollment= get_object_or_404(Enrollments, id=id)
        enrollment.is_archived = True
        enrollment.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": True})


    return redirect('enrollment_list')




def batch_enrollments(request, batch_id):
    batch = get_object_or_404(Batches, id=batch_id)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        enrollments = Enrollments.objects.filter(
            batch=batch,
            is_archived=False,
            student__role='student'

        )
        
        data = []
        for enrollment in enrollments:
            data.append({
                'id': enrollment.id,
                'count': enrollment.id,  
                'student_name': enrollment.student.get_full_name() or enrollment.student.username,
                'batch_name': enrollment.batch.batch_name,
                'course_name': enrollment.batch.course.course_name,
                'enrollment_id': enrollment.id
            })
        
        return JsonResponse({'data': data})
    
    context = {
        "batch": batch,
    }
    return render(request, "batch_enrollments.html", context)








   

def add_marks(request, enrollment_id):
    enrollment = get_object_or_404(Enrollments, id=enrollment_id)
    batch = enrollment.batch
    course = batch.course

    
    if request.method == "POST":
        try:
            
            subjects = Subjects.objects.filter(courses=course, is_archive=False)
            
            
            for subject in subjects:
                mark_field = f"mark_{subject.id}"
                mark_value = request.POST.get(mark_field)
                
                if mark_value and mark_value.strip():
                    try:
                        mark_int = int(mark_value)
                        if 0 <= mark_int <= 100:
                            Marks.objects.update_or_create(
                                enrollment=enrollment,
                                course=course,
                                subject=subject,
                                defaults={'mark': mark_int}
                            )
                    except ValueError:
                        continue
            
            return JsonResponse({
                "status": "success",
                "message": "Marks saved successfully!"
            })
            
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            })
    
   
    subjects = Subjects.objects.filter(courses=course, is_archive=False)
    
    existing_marks = Marks.objects.filter(enrollment=enrollment)
    marks_dict = {mark.subject_id: mark.mark for mark in existing_marks}

    all_marks = [mark.mark for mark in existing_marks]
    avg_mark = sum(all_marks) / len(all_marks) if all_marks else 0
    
    subjects_data = []
    for subject in subjects:
        subjects_data.append({
            "id": subject.id,
            "name": subject.subject_name,
            "mark": marks_dict.get(subject.id), 
        })
    
    
    student_display_name = enrollment.student.get_full_name() or enrollment.student.username
    
    return JsonResponse({
        "student_id": enrollment.student.id,
        "student_name": student_display_name,  
        "batch_name": batch.batch_name,
        "course_name": course.course_name,
        "subjects": subjects_data,
        "average_mark": round(avg_mark, 2)
    })

# ############################################PDF Download ######################################


def download_result_pdf(request, enrollment_id):
    
    enrollment = get_object_or_404(Enrollments, id=enrollment_id, student__role='student')
    batch = enrollment.batch
    course = batch.course
    student = enrollment.student
    
   
    marks = Marks.objects.filter(enrollment=enrollment).select_related('subject')
    
    
    total_marks = sum(mark.mark for mark in marks)
    total_subjects = marks.count()
    percentage = (total_marks / (total_subjects * 100)) * 100 if total_subjects > 0 else 0
    
    
    if percentage >= 35:
        status = "PASS"
        status_color = colors.green
    else:
        status = "FAIL"
        status_color = colors.red
    
    
    buffer = io.BytesIO()
    
    
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    
    elements = []
    
    
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
   
    center_style = ParagraphStyle(
        'CenterStyle',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=12
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=16,
        textColor=colors.HexColor('#0d6efd'),
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    
    institute_name = Paragraph("Training Institute", header_style)
    elements.append(institute_name)
    
    
    result_title = Paragraph("STUDENT RESULT CARD", title_style)
    elements.append(result_title)
    elements.append(Spacer(1, 20))
    
    
    info_data = [
        ["Student Name:", student.get_full_name() or student.username],
        ["Batch:", batch.batch_name],
        ["Course:", course.course_name],
        ["Date:", datetime.now().strftime("%d-%m-%Y")],
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 2.0*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    
    marks_title = Paragraph("Marks", heading_style)
    elements.append(marks_title)
    elements.append(Spacer(1, 10))
    
    
    table_data = []
    table_data.append(["Sr No.", "Subject", "Marks", "Max Marks", "Percentage", "Grade"])
    
    for idx, mark in enumerate(marks, 1):
        subject = mark.subject
        marks_obtained = mark.mark
        max_marks = 100
        subject_percentage = (marks_obtained / max_marks) * 100
        
        
        if subject_percentage >= 90:
            grade = "A+"
        elif subject_percentage >= 80:
            grade = "A"
        elif subject_percentage >= 70:
            grade = "B"
        elif subject_percentage >= 60:
            grade = "C"
        elif subject_percentage >= 35:
            grade = "D"
        else:
            grade = "F"
        
        table_data.append([
            idx,
            subject.subject_name,
            marks_obtained,
            max_marks,
            f"{subject_percentage:.1f}%",
            grade
        ])
    
    
    if total_subjects > 0:
        table_data.append([
            "",
            "TOTAL",
            total_marks,
            total_subjects * 100,
            f"{percentage:.1f}%",
            ""
        ])
    
    
    marks_table = Table(table_data, colWidths=[0.5*inch, 2*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
    marks_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e2e3e5')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
    ]))
    
    elements.append(marks_table)
    elements.append(Spacer(1, 20))
    
    
    summary_data = [
        ["Total Subjects:", str(total_subjects)],
        ["Total Marks Obtained:", f"{total_marks}/{total_subjects * 100}"],
        ["Percentage:", f"{percentage:.2f}%"],
        ["Status:", status],
    ]
    
    summary_table = Table(summary_data, colWidths=[1.5*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('TEXTCOLOR', (1, 3), (1, 3), status_color),
        ('FONTNAME', (1, 3), (1, 3), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 3), (1, 3), 12),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # # Signature Section
    # signature_data = [
    #     ["", "", "Authorized Signature"],
    #     ["", "", "_________________"],
    #     ["", "", "(Coordinator)"],
    # ]
    
    # signature_table = Table(signature_data, colWidths=[2*inch, 2*inch, 2*inch])
    # signature_table.setStyle(TableStyle([
    #     ('ALIGN', (2, 0), (2, -1), 'CENTER'),
    #     ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    #     ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
    #     ('FONTSIZE', (2, 0), (2, 0), 10),
    #     ('FONTSIZE', (2, 1), (2, 2), 9),
    # ]))
    
    # elements.append(signature_table)
    # elements.append(Spacer(1, 20))
    
    # # Footer
    # footer_text = f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    # footer = Paragraph(footer_text, center_style)
    # elements.append(footer)
    
    
    doc.build(elements)
    
    
    pdf = buffer.getvalue()
    buffer.close()
    
    
    response = HttpResponse(content_type='application/pdf')
    filename = f"Result_{student.get_full_name() or student.username}_{batch.batch_name}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf)
    
    return response


############################Email and password########################################
# @login_required
# def change_email(request):
#     if request.method == 'POST':
#         new_email = request.POST.get('email')
        
        
#         if User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
#             messages.error(request, 'This email is already in use by another account.')
#             return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
        
        
#         request.user.email = new_email
#         request.user.save()
#         messages.success(request, 'Your email has been updated successfully.')
        
#     return redirect(request.META.get('HTTP_REFERER', 'dashboard'))




@login_required
@require_POST
def change_email(request):
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            new_email = data.get('email')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    else:
        new_email = request.POST.get('email')
    
   
    if not new_email:
        messages.error(request, 'Email address is required.')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Email address is required'}, status=400)
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
    
   
    if User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
        messages.error(request, 'This email is already in use by another account.')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'This email is already in use'}, status=400)
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
    
    
    request.user.email = new_email
    request.user.save()
    
    
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Your email has been updated successfully.',
            'new_email': new_email
        })
    
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))





@login_required
@require_POST
def change_password(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            current_password = data.get('current_password')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    else:
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
    
    
    if not all([current_password, new_password, confirm_password]):
        return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)
    
    
    if not request.user.check_password(current_password):
        return JsonResponse({'success': False, 'error': 'Current password does not match'}, status=400)
    
   
    if current_password == new_password:
        return JsonResponse({'success': False, 'error': 'New password must be different from current password'}, status=400)
    
   
    if new_password != confirm_password:
        return JsonResponse({'success': False, 'error': 'New passwords do not match'}, status=400)
    
    
    if len(new_password) < 8:
        return JsonResponse({'success': False, 'error': 'Password must be at least 8 characters long'}, status=400)
    
    
    request.user.set_password(new_password)
    request.user.save()
    
    
    update_session_auth_hash(request, request.user)
    
    
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Your password has been updated successfully.'
        })
    
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

#########################################Upload CSV################################

# def upload_students_csv(request):

#     if request.method == "POST":

#         csv_file = request.FILES.get("csv_file")

        
#         if not csv_file:
#             messages.error(request, "No file uploaded!")
#             return redirect("upload_students_csv")

        
#         if not csv_file.name.endswith(".csv"):
#             messages.error(request, "Only CSV files are allowed!")
#             return redirect("upload_students_csv")

        
#         decoded_file = csv_file.read().decode("utf-8").splitlines()
#         reader = csv.DictReader(decoded_file)

#         created_count = 0
#         reader.fieldnames = [h.strip() for h in reader.fieldnames]

#         for row in reader:

#             first_name = row["First Name"].strip()
#             last_name = row["Last Name"].strip()
#             email = row["email"].strip()
#             batch_id = row["Batch_id"].strip()

#             username = email
#             raw_password = f"{first_name}@123"

            
#             try:
#                 batch = Batches.objects.get(id=batch_id)
#             except Batches.DoesNotExist:
#                 continue  

            
#             if User.objects.filter(email=email).exists():
#                 continue

            
#             student = User.objects.create(
#                 first_name=first_name,
#                 last_name=last_name,
#                 email=email,
#                 username=username,
#                 role="student",
#                 nationality="India",
#                 password=make_password(raw_password),
#             )

            
#             Enrollments.objects.create(
#                 batch=batch,
#                 student=student
#             )

#             created_count += 1

#         messages.success(
#             request,
#             f"{created_count} students uploaded and enrolled successfully!"
#         )

#         return redirect("upload_students_csv")

#     return render(request, "admin/upload_students.html")







def upload_students_csv(request):

    if request.method == "POST":

        csv_file = request.FILES.get("csv_file")

        if not csv_file:
            return JsonResponse({
                "success": False,
                "message": "No file uploaded!"
            })

        if not csv_file.name.endswith(".csv"):
            return JsonResponse({
                "success": False,
                "message": "Only CSV files are allowed!"
            })

        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        
        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        created_count = 0
        errors = []
        row_number = 1

        for row in reader:
            row_number += 1

            first_name = row.get("First Name", "").strip()
            last_name  = row.get("Last Name", "").strip()
            email      = row.get("email", "").strip()
            batch_id   = row.get("Batch_id", "").strip()

            student_name = f"{first_name} {last_name}".strip()
            if not student_name:
                student_name = "Unknown Student"


           
            # if not first_name or not last_name or not email or not batch_id:
            #     errors.append(f"Row {row_number}: Incomplete student info.")
            #     continue
            missing_fields = []

            if not first_name:
                missing_fields.append("First Name")
            if not last_name:
                missing_fields.append("Last Name")
            if not email:
                missing_fields.append("Email")
            if not batch_id:
                missing_fields.append("Batch ID")

            if missing_fields:
                errors.append(
                    f"Row {row_number}: Missing {', '.join(missing_fields)}."
                )
                continue


           
            try:
                batch = Batches.objects.get(id=batch_id)
            except Batches.DoesNotExist:
                errors.append(f"Cannot add {student_name}: Batch ID {batch_id} does not exist.")

                continue

            
            if User.objects.filter(email=email).exists():
                errors.append(f"Cannot add {student_name}: Email ({email}) already exists.")

                continue

            
            raw_password = f"{first_name}@123"

            student = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email,
                role="student",
                nationality="India",
                password=make_password(raw_password),
            )

            
            Enrollments.objects.create(
                batch=batch,
                student=student
            )

            created_count += 1

        return JsonResponse({
            "success": True,
            "created": created_count,
            "errors": errors
        })

    return render(request, "admin/upload_students.html")





















###########################Before mapping teachers#######################
# def subject_teacher_list(request):

#     course_id = request.GET.get("course_id")
#     course = Courses.objects.get(id=course_id)

#     subjects_data = []

    
#     for sub in course.subjects.all():

        
#         teachers = User.objects.filter(
#             role="teacher",
#             subjects=sub
#         )

#         subjects_data.append({
#             "id": sub.id,
#             "name": sub.subject_name,
#             "teachers": [
#                 {
#                     "id": t.id,
#                     "name": f"{t.first_name} {t.last_name}"
#                 }
#                 for t in teachers
#             ]
#         })

#     return JsonResponse({"subjects": subjects_data})



# def add_batch(request):
#     if request.method=='POST':
#         batch_name = request.POST.get('batch_name')
#         start_date = request.POST.get("start_date")
#         duration = request.POST.get("duration")
#         course_id = request.POST.get("course")

#         course = Courses.objects.get(id=course_id)

#         batch=Batches.objects.create(
#             batch_name=batch_name,
#             course=course,
#             start_date=start_date,
#             duration=duration
#         )
#         batch.save()

        
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             return JsonResponse({"success":True})
#     return redirect('batch_list')













# def batch_enrollments(request, batch_id):
#     batch = get_object_or_404(Batches, id=batch_id)

#     enrollments = Enrollments.objects.filter(
#         batch=batch,
#         is_archived=False
#     )

#     context = {
#         "batch": batch,
#         "enrollments": enrollments
#     }

#     return render(request, "batch_enrollments.html", context)



# def add_marks(request, enrollment_id):
#     enrollment = get_object_or_404(Enrollments, id=enrollment_id)
#     batch = enrollment.batch
#     course = batch.course
    
#     if request.method == "POST":
#         try:
            
#             subjects = Subjects.objects.filter(courses=course, is_archive=False)
            
            
#             for subject in subjects:
#                 mark_field = f"mark_{subject.id}"
#                 mark_value = request.POST.get(mark_field)
                
#                 if mark_value and mark_value.isdigit():
#                     mark_obj, created = Marks.objects.update_or_create(
#                         enrollment=enrollment,
#                         course=course,
#                         subject=subject,
#                         defaults={'mark': int(mark_value)}
#                     )
            
#             return JsonResponse({
#                 "status": "success",
#                 "message": "Marks saved successfully!"
#             })
            
#         except Exception as e:
#             return JsonResponse({
#                 "status": "error",
#                 "message": f"An error occurred: {str(e)}"
#             })
    
    
#     subjects = Subjects.objects.filter(courses=course, is_archive=False)
    
    
#     existing_marks = Marks.objects.filter(enrollment=enrollment)
#     marks_dict = {mark.subject.id: mark.mark for mark in existing_marks}

#     all_marks = [mark.mark for mark in existing_marks]
#     avg_mark = sum(all_marks) / len(all_marks) if all_marks else 0
    
#     subjects_data = []
#     for subject in subjects:
#         subjects_data.append({
#             "id": subject.id,
#             "name": subject.subject_name,
#             "mark": marks_dict.get(subject.id), 
#         })
    
#     return JsonResponse({
#         "student_id":enrollment.student.id,
#         "student_name": enrollment.student.user_name,
#         "batch_name": batch.batch_name,
#         "course_name": course.course_name,
#         "subjects": subjects_data,
#         "average_mark": round(avg_mark, 2)
#     })

    


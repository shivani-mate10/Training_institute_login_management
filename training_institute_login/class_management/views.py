from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import Registerform ,subjectform,courseform
from django.contrib.auth.decorators import login_required
from .models import User,Subjects,Courses, Batches
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import logout
from django.core.paginator import Paginator


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




@login_required
def dashboard_view(request):
    return render(request, "dashboard.html")


@login_required
def users_list(request):
    users = User.objects.filter(is_archived=False).values(
        "id", "first_name", "last_name", "role"
    )

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
###################################Batches#################################
def batch_list(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        batches = Batches.objects.filter(is_archived=False)
         
        
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
    
    
    
    courses = Courses.objects.filter(is_archived=False)  # Get all courses for the dropdown
    return render(request, 'batch_list.html', {'courses': courses})

def add_batch(request):
    if request.method=='POST':
        batch_name = request.POST.get('batch_name')
        start_date = request.POST.get("start_date")
        duration = request.POST.get("duration")
        course_id = request.POST.get("course")

        course = Courses.objects.get(id=course_id)

        batch=Batches.objects.create(
            batch_name=batch_name,
            course=course,
            start_date=start_date,
            duration=duration
        )
        batch.save()

        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success":True})
    return redirect('batch_list')



def subject_teacher_list(request):
    course_id = request.GET.get("course_id")
    batch_id = request.GET.get("batch_id")
    course = Courses.objects.get(id=course_id)



    return JsonResponse({"course": course})



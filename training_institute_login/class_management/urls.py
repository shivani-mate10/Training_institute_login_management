from django.urls import path
from .views import register_user,login_user,dashboard_view,logout_user,add_user,delete_user,update_user,users_list
from .views import subject_list ,course_list,add_course,delete_course,update_course,add_subject,delete_subject,update_subject
from .views import subject_list_ajax,batch_list,add_batch,subject_teacher_list,delete_batch,update_batch,enrollment_list,add_enrollment,delete_enrollment
from .views import batch_enrollments,add_marks,download_result_pdf,user_management,change_email, change_password


urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("users/", user_management, name="user_management"), 
    path("register/", register_user, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("users/ajax/", users_list, name="users_ajax"),
    path("users/add/ajax/", add_user, name="add_user_ajax"),
    path('delete-user/<int:id>/', delete_user, name='delete_user'),
    path('update-user/<int:id>/', update_user, name='update_user'),
  


    path("subject/", subject_list,name="subject_list"),
    path("subject/add/", add_subject,name="add_subject"),
    path("update-subject/<int:id>/",update_subject,name="update_subject"),
    path("delete-subject/<int:id>/",delete_subject,name="delete_subject"),

    path("course/", course_list,name="course_list"),
    path("course/add/", add_course,name="add_course"),
    path('delete-course/<int:id>/', delete_course, name='delete_course'),
    path('update-course/<int:id>/', update_course, name='update_course'),\
    
    path("ajax/subjects/", subject_list_ajax, name="subject_list_ajax"),

    path("batch/", batch_list,name="batch_list"),
    path("batch/add/", add_batch, name="add_batch"),
    path("ajax/subject-teacher-list/",subject_teacher_list, name="subject_teacher_list"),
    path("delete-batch/<int:id>/",delete_batch,name="delete_batch"),
    path("update-batch/<int:id>/",update_batch,name="update_batch"),


    path("enrollment/", enrollment_list,name="enrollment_list"),
    path("enrollment/add/", add_enrollment,name="add_enrollment"),
    path("delete-enrollment/<int:id>/",delete_enrollment,name="delete_enrollment"),

    path("batch/enrollments/<int:batch_id>/", batch_enrollments, name="batch_enrollments"),


    path("marks/add/<int:enrollment_id>/", add_marks, name="add_marks"),

    
    path('marks/download/<int:enrollment_id>/', download_result_pdf, name='download_result_pdf'),

    path('change-email/',change_email, name='change_email'),
    path('change-password/', change_password, name='change_password'),
 
]

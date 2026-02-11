from django.urls import path
from .views import register_user,login_user,dashboard_view,logout_user,users_list,add_user,delete_user,update_user
from .views import subject_list ,course_list,add_course,delete_course,update_course,add_subject,delete_subject,update_subject
from .views import subject_list_ajax
urlpatterns = [
    path("", dashboard_view, name="dashboard"),
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


    
    
]

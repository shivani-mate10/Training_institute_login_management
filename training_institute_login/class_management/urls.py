from django.urls import path
from .views import register_user,login_user,dashboard_view,logout_user,users_list,add_user,delete_user,update_user
from .views import subject_list,add_subject,update_subject,delete_subject,course_list,add_course,delete_course
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
    path("subject/update/<int:id>",update_subject,name="update_subject"),
    path("subject/delete/<int:id>",delete_subject,name="delete_subject"),

    path("course/", course_list,name="course_list"),
    path("course/add/", add_course,name="add_course"),
    path('delete-course/<int:id>/', delete_course, name='delete_course'),

    
    
]

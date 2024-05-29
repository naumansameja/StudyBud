from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("room/<str:pk>/", views.room_page, name="room"),
    path("create-room/", views.create_room, name="create-room"),
    path("update-room/<str:pk>/", views.update_room, name="update-room"),
    path("delete/<str:pk>/", views.delete_room, name="delete-room"),
    path("delete-message/<str:origin>/<str:pk>/", views.delete_message, name="delete-message"),
    path("login", views.user_login, name="login"),
    path("register", views.user_register, name="register"),
    path("logout", views.user_logout, name="logout"),
    path("user-profile/<str:pk>/", views.user_profile, name='user-profile'),
    path("update-user/", views.update_user, name="update-user"),
    path("topics/", views.topics_page, name="topics"),
    path("activity/", views.activity_page, name="activity"),
    path('upload/<str:pk>', views.upload_picture, name='upload'),
    path('password-change/<str:pk>', views.change_password, name='change-password'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('reset-password/<uidb64>/<token>', views.reset_password, name='reset-password'),
    path('get-email', views.reset_password_email_getter, name='get-email'),
    path('add-participant<str:roomid>/<str:userid>', views.join_room, name='add-participant'),
    

]
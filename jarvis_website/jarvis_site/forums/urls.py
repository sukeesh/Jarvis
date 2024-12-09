from django.urls import path
from . import views

urlpatterns = [
    path('', views.forums_home, name='forums_home'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('', views.forums_home, name='forums'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('reply/<int:reply_id>/delete/', views.delete_reply, name='delete_reply'),
    path('my_posts/', views.my_posts, name='my_posts'),
    path('my_replies/', views.my_replies, name='my_replies'),
    path('my_likes/', views.my_likes, name='my_likes'),
]

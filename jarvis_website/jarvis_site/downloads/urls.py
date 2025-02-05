from django.urls import path
from . import views
from downloads import views as download_views

urlpatterns = [
    path('', views.home, name='home'),  # Homepage
    path('downloads/', views.downloads, name='downloads'),  # Downloads page
    path('account/', views.account_page, name='account'),
    path('update_email/', views.update_email, name='update_email'),
    path('change_password/', views.change_password, name='change_password'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('download-jarvis-zip/', download_views.create_and_download_zip,
         name='download_jarvis_zip'),
    # path('forums/', views.forums_home, name='forums_home'),
]

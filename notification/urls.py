from django.urls import path

from notification import views

urlpatterns = [

    path('register/', views.RegisterView.as_view()),

    path('inactivity/', views.InactivityView.as_view()),

    path('message/', views.MessageView.as_view()),

]

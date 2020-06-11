from django.urls import path

from companion import views

urlpatterns = [
    path('request/', views.RequestView.as_view()),
    path('request/<int:id>/', views.RemoveRequestView.as_view()),
    path('request-detail/<int:request_id>/', views.RequestDetailView.as_view()),
    path('find/', views.FindRequestView.as_view()),
    path('interest/', views.CompanionView.as_view()),
    path('completed/', views.CompletedView.as_view()),
    path('companions/<int:request_id>/', views.CompanionRequestView.as_view()),
    path('list/', views.RequestList.as_view()),
    path('feedback/', views.FeedbackView.as_view()),
    path('companion-status/', views.CompanionStatusView.as_view()),
]

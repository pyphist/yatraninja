from django.urls import path

from user import views

urlpatterns = [
    path('send-otp/', views.SendOTP.as_view()),
    path('verify-otp/', views.VerifyOTP.as_view()),
    path('send-otp-login/', views.SendOTPLogin.as_view()),
    path('otp-login/', views.VerifyOTPLogin.as_view()),
    path('sign-up/', views.SignUpView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('reset-password/', views.ResetPasswordView.as_view()),
    path('social-login/', views.SocialLoginView.as_view()),
    path('profile/', views.ProfileView.as_view()),
    path('profile-picture/', views.ProfilePictureView.as_view(), name='profile-picture'),
    path('ban/', views.BanUser.as_view()),
    path('lift-ban/', views.LiftBan.as_view()),
    path('users/', views.UsersView.as_view()),
    path('last-login/', views.LastLoginView.as_view()),
    path('refresh-token/', views.RefreshTokenView.as_view()),
]

from django.urls import path

from . import views



urlpatterns = [
    path('api/auth/google', views.google_auth , name='Authentication with google'),
    path('api/auth/sing-in', views.SingInView.as_view(), name='Authentication with email'),
    path('api/auth/sing-up', views.CreateAccountAPIView.as_view(), name='Create new account'),
    path('api/auth/token/refresh', views.TokenRefresh.as_view(), name='token_refresh'),
    path('api/auth/verify-reset-code', views.VerifyResetCodeView.as_view(), name='verify-reset-code'),
     path('api/auth/confirm-email', views.ConfirmEmailView.as_view(), name='change-password'),
    path('api/auth/request-reset-code', views.RequestResetCodeView.as_view(), name='request-reset-code'),
    path('api/auth/change-password', views.ChangePasswordView.as_view(), name='change-password'),
]
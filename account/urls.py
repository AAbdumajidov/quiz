from django.urls import path
from .views import LoginView, RegisterView, MyProfileRUDAPIView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('register/', RegisterView.as_view()),
    path('my_profile/<int:pk>', MyProfileRUDAPIView.as_view()),
]
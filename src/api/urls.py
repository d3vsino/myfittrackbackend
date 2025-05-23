from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import  AiView, CalorieLogViewSet, UserProfileView, RegisterView, ChatHistoryView, MacroFromImageView
from rest_framework.routers import DefaultRouter

calorie_router = DefaultRouter()
calorie_router.register(r'calorie-logs', CalorieLogViewSet, basename='calorie-log')

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('ai/', AiView.as_view()),
    path('ai/chat-history/', ChatHistoryView.as_view()),
    path('token/obtain/', TokenObtainPairView.as_view()),
    path('analyze-meal/', MacroFromImageView.as_view(), name='analyze-meal'),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('', include(calorie_router.urls)),
    path('profile/', UserProfileView.as_view()),
]

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import MedicalExamViewSet, PatientViewSet, RegisterUserAPIView

router = DefaultRouter()
router.register('patients', PatientViewSet, basename='patient')
router.register('medical-exams', MedicalExamViewSet, basename='medicalexam')

urlpatterns = [
    path('auth/register/', RegisterUserAPIView.as_view(), name='auth-register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]

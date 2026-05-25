from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MedicalExam, Patient
from .serializers import MedicalExamSerializer, PatientSerializer, UserRegistrationSerializer


class RegisterUserAPIView(APIView):
    """Endpoint para registrar un nuevo usuario mediante JWT."""

    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PatientViewSet(viewsets.ModelViewSet):
    """CRUD completo para pacientes."""

    queryset = Patient.objects.all().order_by('-created_at')
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]


class MedicalExamViewSet(viewsets.ModelViewSet):
    """CRUD completo para exámenes médicos."""

    queryset = MedicalExam.objects.select_related('patient').all().order_by('-uploaded_at')
    serializer_class = MedicalExamSerializer
    permission_classes = [IsAuthenticated]

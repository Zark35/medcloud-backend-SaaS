from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MedicalExam, Patient
from .serializers import MedicalExamSerializer, PatientSerializer, UserRegistrationSerializer


class HealthCheckAPIView(APIView):
    """Health check para Docker, Nginx y Render."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'ok', 'service': 'medcloud-api'})


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


@extend_schema_view(
    list=extend_schema(summary='Listar exámenes médicos'),
    retrieve=extend_schema(summary='Obtener un examen médico'),
    create=extend_schema(
        summary='Crear examen médico con archivo',
        description=(
            'Envía `multipart/form-data` con los campos del examen y el archivo '
            'en `exam_file`. Formatos permitidos: PDF, JPG, JPEG, PNG, WEBP (máx. 10 MB).'
        ),
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'patient': {'type': 'integer', 'example': 1},
                    'title': {'type': 'string', 'example': 'Radiografía de tórax'},
                    'description': {'type': 'string', 'example': 'Control anual'},
                    'exam_file': {'type': 'string', 'format': 'binary'},
                },
                'required': ['patient', 'title', 'exam_file'],
            }
        },
        responses={201: MedicalExamSerializer},
    ),
    update=extend_schema(
        summary='Actualizar examen médico',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'patient': {'type': 'integer'},
                    'title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'exam_file': {'type': 'string', 'format': 'binary'},
                },
            }
        },
    ),
    partial_update=extend_schema(
        summary='Actualizar parcialmente examen médico',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'patient': {'type': 'integer'},
                    'title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'exam_file': {'type': 'string', 'format': 'binary'},
                },
            }
        },
    ),
    destroy=extend_schema(summary='Eliminar examen médico'),
)
class MedicalExamViewSet(viewsets.ModelViewSet):
    """CRUD completo para exámenes médicos."""

    queryset = MedicalExam.objects.select_related('patient').all().order_by('-uploaded_at')
    serializer_class = MedicalExamSerializer
    permission_classes = [IsAuthenticated]

    parser_classes = [MultiPartParser, FormParser]

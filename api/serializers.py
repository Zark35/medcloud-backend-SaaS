from pathlib import Path

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import MedicalExam, Patient

ALLOWED_EXAM_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.webp'}
MAX_EXAM_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializador para registrar usuarios mediante la API."""
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class PatientSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Patient."""

    class Meta:
        model = Patient
        fields = ['id', 'full_name', 'age', 'gender', 'medical_history', 'created_at']
        read_only_fields = ['id', 'created_at']


class MedicalExamSerializer(serializers.ModelSerializer):
    """Serializador para el modelo MedicalExam con upload de archivo."""

    patient_name = serializers.ReadOnlyField(source='patient.full_name')
    exam_file = serializers.FileField(write_only=True, required=False)
    exam_file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MedicalExam
        fields = [
            'id',
            'patient',
            'patient_name',
            'title',
            'description',
            'exam_file',
            'exam_file_url',
            'uploaded_at',
        ]
        read_only_fields = ['id', 'patient_name', 'exam_file_url', 'uploaded_at']

    def get_exam_file_url(self, obj):
        if not obj.exam_file:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.exam_file.url)
        return obj.exam_file.url

    def validate_exam_file(self, value):
        extension = Path(value.name).suffix.lower()
        if extension not in ALLOWED_EXAM_EXTENSIONS:
            allowed = ', '.join(sorted(ALLOWED_EXAM_EXTENSIONS))
            raise serializers.ValidationError(
                f'Tipo de archivo no permitido. Extensiones válidas: {allowed}'
            )
        if value.size > MAX_EXAM_FILE_SIZE_BYTES:
            raise serializers.ValidationError('El archivo no puede superar 10 MB.')
        return value

    def validate(self, attrs):
        if self.instance is None and not attrs.get('exam_file'):
            raise serializers.ValidationError({'exam_file': 'Este campo es obligatorio.'})
        return attrs

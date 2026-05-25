from django.contrib.auth.models import User
from rest_framework import serializers

from .models import MedicalExam, Patient


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
    """Serializador para el modelo MedicalExam."""
    patient_name = serializers.ReadOnlyField(source='patient.full_name')

    class Meta:
        model = MedicalExam
        fields = ['id', 'patient', 'patient_name', 'title', 'description', 'exam_file', 'uploaded_at']
        read_only_fields = ['id', 'patient_name', 'uploaded_at']

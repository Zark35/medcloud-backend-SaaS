from django.db import models


class Patient(models.Model):
    """Representa un paciente dentro de MedCloud."""

    class GenderChoices(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        OTHER = 'other', 'Other'

    full_name = models.CharField(max_length=255)
    age = models.PositiveSmallIntegerField()
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    medical_history = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.full_name} ({self.age})'


class MedicalExam(models.Model):
    """Registra los exámenes médicos asociados a un paciente."""

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='medical_exams',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    exam_file = models.FileField(upload_to='medical_exams/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} for {self.patient.full_name}'

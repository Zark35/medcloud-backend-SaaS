from django.contrib import admin

from .models import MedicalExam, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'gender', 'created_at')
    search_fields = ('full_name', 'medical_history')
    list_filter = ('gender',)


@admin.register(MedicalExam)
class MedicalExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'uploaded_at')
    search_fields = ('title', 'description')
    list_filter = ('uploaded_at',)

from django.contrib import admin
from .models import PipelineImage


@admin.register(PipelineImage)
class PipelineImageAdmin(admin.ModelAdmin):
	list_display = ('id', 'image', 'uploaded_at')
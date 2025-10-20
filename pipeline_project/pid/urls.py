from django.urls import path
from .views import PipelineDetectionView

urlpatterns = [
    path('pipeline/', PipelineDetectionView.as_view(), name='pipeline-detection'),
]
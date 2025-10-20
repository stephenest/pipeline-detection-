from django.db import models


class PipelineImage(models.Model):
	"""Stores uploaded images for pipeline detection (optional)."""
	image = models.ImageField(upload_to='uploads/')
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'PipelineImage {self.id} ({self.image.name})'
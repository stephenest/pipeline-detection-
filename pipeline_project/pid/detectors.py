from django.core.files.storage import default_storage
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import detect_pipelines

class PipelineDetectionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image provided.'}, status=400)

        image_file = request.FILES['image']

        if not image_file.name.endswith(('.png', '.jpg', '.jpeg')):
            return JsonResponse({'error': 'Invalid file type. Only PNG and JPG images are accepted.'}, status=400)

        # Save the uploaded image temporarily
        image_path = default_storage.save(image_file.name, image_file)

        try:
            # Call the detect_pipelines function
            pipelines = detect_pipelines(image_path)
            return JsonResponse({'pipelines': pipelines}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            # Clean up the temporary file
            default_storage.delete(image_path)
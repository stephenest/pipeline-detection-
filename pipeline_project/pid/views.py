from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import detect_pipelines
import os
import tempfile
from django.core.files.uploadedfile import InMemoryUploadedFile


class PipelineDetectionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        if 'image' not in request.FILES:
            return Response({"error": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES['image']

        # Basic file type check
        content_type = getattr(image, 'content_type', '')
        if not content_type.startswith('image/'):
            return Response({"error": "Uploaded file is not an image."}, status=status.HTTP_400_BAD_REQUEST)

        # Save input to a temporary file
        tmp_dir = tempfile.gettempdir()
        tmp_path = os.path.join(tmp_dir, image.name)
        with open(tmp_path, 'wb') as f:
            if isinstance(image, InMemoryUploadedFile):
                for chunk in image.chunks():
                    f.write(chunk)
            else:
                for chunk in image.chunks():
                    f.write(chunk)

        try:
            visualize = request.query_params.get('visualize', 'false').lower() in ('1', 'true', 'yes')
            result = detect_pipelines(tmp_path, visualize=visualize)
            if visualize:
                pipelines, visual_b64 = result
            else:
                pipelines = result

            response = {'pipelines': pipelines}
            if visualize:
                response['visualization'] = visual_b64

            return Response(response)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
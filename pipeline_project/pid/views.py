from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import detect_pipelines
import os
import tempfile
from pdf2image import convert_from_path


class PipelineDetectionView(APIView):
    """API view for detecting pipelines in images or PDFs."""

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        """Handle POST requests with image/PDF files."""
        print(f"Request files: {request.FILES}")  # Debug print
        print(f"Request data: {request.data}")  # Debug print
        
        if 'image' not in request.FILES:
            return Response({
                "error": "No file uploaded with key 'image'",
                "available_files": list(request.FILES.keys())
            }, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['image']
        print(f"Received file: {uploaded_file.name}, size: {uploaded_file.size}, content type: {uploaded_file.content_type}")  # Debug print

        # Accept both images and PDFs
        content_type = getattr(uploaded_file, 'content_type', '')
        is_pdf = content_type == 'application/pdf' or uploaded_file.name.lower().endswith('.pdf')

        if not (content_type.startswith('image/') or is_pdf):
            return Response({"error": "Uploaded file must be an image or PDF."}, status=status.HTTP_400_BAD_REQUEST)

        # Save input to a temporary file
        tmp_dir = tempfile.gettempdir()
        base_name = f"upload_{abs(hash(uploaded_file.name))}"
        ext = os.path.splitext(uploaded_file.name)[1] or ('.pdf' if is_pdf else '.png')
        tmp_path = os.path.join(tmp_dir, base_name + ext)

        try:
            # Write uploaded file to disk
            with open(tmp_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
                f.flush()
                os.fsync(f.fileno())

            # If PDF, convert first page to PNG
            if is_pdf:
                pages = convert_from_path(tmp_path, first_page=1, last_page=1)
                if not pages:
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                    return Response({'error': 'Could not convert PDF to image'}, status=status.HTTP_400_BAD_REQUEST)

                png_path = os.path.join(tmp_dir, base_name + '.png')
                pages[0].save(png_path, 'PNG')
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
                tmp_path = png_path

            visualize = request.query_params.get('visualize', 'false').lower() in ('1', 'true', 'yes')
            result = detect_pipelines(tmp_path, visualize=visualize)

            if visualize and isinstance(result, tuple) and len(result) == 2:
                pipelines, visual_b64 = result
            else:
                pipelines = result
                visual_b64 = None

            if not isinstance(pipelines, list):
                return Response({'error': 'Invalid pipeline detection result'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            resp = {'pipelines': pipelines}
            if visual_b64:
                resp['visualization'] = visual_b64
            return Response(resp, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        finally:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass




                # Accept both images and PDFs
                content_type = getattr(uploaded_file, 'content_type', '')
                is_pdf = content_type == 'application/pdf' or uploaded_file.name.lower().endswith('.pdf')

                if not (content_type.startswith('image/') or is_pdf):
                    return Response({"error": "Uploaded file must be an image or PDF."}, status=status.HTTP_400_BAD_REQUEST)

                # Save input to a temporary file
                file_ext = os.path.splitext(uploaded_file.name)[1].lower() or '.bin'
                tmp_dir = tempfile.gettempdir()
                tmp_path = os.path.join(tmp_dir, f'upload_{abs(hash(uploaded_file.name))}{file_ext}')

                try:
                    # Write file content to disk
                    with open(tmp_path, 'wb') as f:
                        for chunk in uploaded_file.chunks():
                            f.write(chunk)
                        f.flush()
                        try:
                            os.fsync(f.fileno())
                        except Exception:
                            # fsync may not be available in some environments
                            pass

                    # If PDF, convert first page to PNG
                    if is_pdf:
                        pages = convert_from_path(tmp_path, first_page=1, last_page=1)
                        if not pages:
                            try:
                                os.remove(tmp_path)
                            except Exception:
                                pass
                            return Response({'error': 'Could not convert PDF to image'}, status=status.HTTP_400_BAD_REQUEST)

                        png_path = os.path.join(tmp_dir, f'converted_{abs(hash(uploaded_file.name))}.png')
                        pages[0].save(png_path, 'PNG')
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass
                        tmp_path = png_path

                    visualize = request.query_params.get('visualize', 'false').lower() in ('1', 'true', 'yes')
                    result = detect_pipelines(tmp_path, visualize=visualize)

                    # Support functions that return (pipelines, visualization_b64)
                    if visualize and isinstance(result, tuple) and len(result) == 2:
                        pipelines, visual_b64 = result
                    else:
                        pipelines = result
                        visual_b64 = None

                    if not isinstance(pipelines, list):
                        return Response({'error': 'Invalid pipeline detection result'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    resp = {'pipelines': pipelines}
                    if visual_b64:
                        resp['visualization'] = visual_b64
                    return Response(resp, status=status.HTTP_200_OK)

                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

                finally:
                    # attempt cleanup
                    try:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                    except Exception:
                        pass
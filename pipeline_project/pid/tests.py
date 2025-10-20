from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from .utils import detect_pipelines
from io import BytesIO
from PIL import Image, ImageDraw
import tempfile
import os


def create_test_image_with_lines(path):
    img = Image.new('RGB', (400, 300), 'white')
    draw = ImageDraw.Draw(img)
    draw.line((30, 150, 350, 150), fill='black', width=3)
    draw.line((350, 150, 380, 250), fill='black', width=3)
    img.save(path, format='PNG')


class DetectPipelinesTest(TestCase):
    def test_detect_pipelines_unit(self):
        tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        tmp.close()
        try:
            create_test_image_with_lines(tmp.name)
            pipelines = detect_pipelines(tmp.name, visualize=False)
            self.assertIsInstance(pipelines, list)
            self.assertTrue(len(pipelines) >= 1)
            for p in pipelines:
                self.assertIn('source', p)
                self.assertIn('destination', p)
                self.assertEqual(len(p['source']), 2)
                self.assertEqual(len(p['destination']), 2)
        finally:
            try:
                os.remove(tmp.name)
            except Exception:
                pass


class PipelineAPITest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_pipeline_api_upload(self):
        img = Image.new('RGB', (200, 100), 'white')
        draw = ImageDraw.Draw(img)
        draw.line((10, 50, 190, 50), fill='black', width=3)
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        uploaded = SimpleUploadedFile('test.png', buf.read(), content_type='image/png')
        response = self.client.post('/api/pipeline/', {'image': uploaded})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('pipelines', data)
        self.assertIsInstance(data['pipelines'], list)

# Removed older duplicate tests; the file contains self-contained unit and API tests above.
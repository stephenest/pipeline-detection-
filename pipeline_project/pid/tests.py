from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from .utils import detect_pipelines
from pathlib import Path
import os


class DetectPipelinesTest(TestCase):
    def setUp(self):
        # Get path to sample PDF relative to this file
        self.base_dir = Path(__file__).resolve().parent.parent
        self.sample_pdf = os.path.join(self.base_dir, 'sample_input', 'sample_pid8.pdf')

    def test_detect_pipelines_from_pdf(self):
        """Test pipeline detection using the actual sample PDF"""
        self.assertTrue(os.path.exists(self.sample_pdf), f"Sample PDF not found at {self.sample_pdf}")
        
        pipelines = detect_pipelines(self.sample_pdf, visualize=False)
        self.assertIsInstance(pipelines, list)
        self.assertTrue(len(pipelines) >= 1, "Should detect at least one pipeline in sample PDF")
        
        for p in pipelines:
            self.assertIn('source', p)
            self.assertIn('destination', p)
            self.assertEqual(len(p['source']), 2)
            self.assertEqual(len(p['destination']), 2)


class PipelineAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.base_dir = Path(__file__).resolve().parent.parent
        self.sample_pdf = os.path.join(self.base_dir, 'sample_input', 'sample_pid8.pdf')

    def test_pipeline_api_pdf_upload(self):
        """Test the API endpoint with actual sample PDF"""
        self.assertTrue(os.path.exists(self.sample_pdf), f"Sample PDF not found at {self.sample_pdf}")
        
        print(f"Opening sample PDF from: {self.sample_pdf}")  # Debug print
        
        with open(self.sample_pdf, 'rb') as f:
            pdf_content = f.read()
            file_size = len(pdf_content)
            print(f"PDF content read, size: {file_size} bytes")  # Debug print
            
        uploaded = SimpleUploadedFile(
            name='sample_pid8.pdf',
            content=pdf_content,
            content_type='application/pdf'
        )
        print(f"Created SimpleUploadedFile with size: {uploaded.size}")  # Debug print
        
        # Test without visualization first
        response = self.client.post('/api/pipeline/', {'image': uploaded})
        print(f"Response code: {response.status_code}")  # Debug print
        print(f"Response content: {response.content}")  # Debug print
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('pipelines', data)
        self.assertIsInstance(data['pipelines'], list)
        self.assertTrue(len(data['pipelines']) >= 1, "Should detect at least one pipeline")

        # Reset file pointer for second test
        uploaded = SimpleUploadedFile(
            name='sample_pid8.pdf',
            content=pdf_content,
            content_type='application/pdf'
        )
        response = self.client.post('/api/pipeline/?visualize=true', {'image': uploaded})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('pipelines', data)
        self.assertIn('visualization', data)
        self.assertTrue(data['visualization'].startswith('data:image/png;base64,'))

# Removed older duplicate tests; the file contains self-contained unit and API tests above.
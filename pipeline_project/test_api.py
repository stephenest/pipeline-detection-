from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
import os

def test_api():
    client = Client()
    pdf_path = os.path.join(os.path.dirname(__file__), 'sample_input', 'sample_pid8.pdf')
    
    with open(pdf_path, 'rb') as f:
        pdf_content = f.read()
        
    uploaded = SimpleUploadedFile('sample_pid8.pdf', pdf_content, content_type='application/pdf')
    response = client.post('/api/pipeline/', {'image': uploaded})
    print(f'Response content: {response.content.decode()}')
    print(f'Status code: {response.status_code}')

if __name__ == '__main__':
    import django
    django.setup()
    test_api()
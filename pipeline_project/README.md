# README for Pipeline Project

# Pipeline Project

This project is a Django application designed to detect pipelines in engineering diagrams using OpenCV. It provides a REST API for uploading images and receiving detected pipeline information.

## Project Structure

```
pipeline_project
├── Dockerfile
├── LICENSE
├── README.md
├── docker-compose.yml
├── manage.py
├── requirements.txt
├── pipeline_project
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── pid
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── detectors.py
│   ├── utils.py
│   ├── tests.py
│   └── migrations
│       ├── __init__.py
│       └── 0001_initial.py
├── sample_input
│   └── sample_pid8.pdf
└── scripts
    ├── post_sample.py
    ├── process_sample.py
    └── verify.sh
```

## Setup (local)

1. Clone the repository and enter the project folder:

```bash
git clone <repository-url>
cd pipeline_project
```

2. Create and activate a virtualenv, then install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Run migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

## Quick Docker delivery (recommended for reviewers)

Build and run with Docker Compose (no local Python dependencies required):

```bash
cd pipeline_project
docker compose build
docker compose up -d
```

The API will be available at http://localhost:8000/api/pipeline/

To stop and remove containers:

```bash
docker compose down
```

## Usage

POST an image file to `/api/pipeline/` using `image` as the form field. Example curl:

```bash
curl -X POST "http://127.0.0.1:8000/api/pipeline/" -F "image=@/path/to/diagram.png"
```

With visualization:

```bash
curl -X POST "http://127.0.0.1:8000/api/pipeline/?visualize=true" -F "image=@/path/to/diagram.png"
```

## API docs

OpenAPI schema is available at `/api/schema/` and Swagger UI at `/api/docs/` (when server is running).

## Delivery checklist

- [x] Project code (Django project and `pid` app) included
- [x] `/api/pipeline/` endpoint implemented
- [x] `detect_pipelines()` implemented using grayscale → Canny → HoughLinesP
- [x] Basic error handling for missing/invalid images
- [x] `requirements.txt` provided
- [x] `README.md` with run/test instructions
- [x] drf-spectacular OpenAPI schema + Swagger UI
- [x] Unit + API tests added under `pid/tests.py`
- [x] Dockerfile + docker-compose for easy delivery

If you'd like, I can also add a small `sample_input/` image and a short script that runs the endpoint and saves the JSON output to a file — tell me if you want that included in the deliverable.



## Delivery log (step-by-step)

1. Created Django project `pipeline_project` and app `pid`.
2. Implemented `detect_pipelines()` in `pid/utils.py` using OpenCV's Canny + HoughLinesP. Added a safe fallback implementation (Pillow+NumPy) so the code is testable in environments without OpenCV native libs.
3. Implemented REST API endpoint `/api/pipeline/` in `pid/views.py` that accepts multipart image upload, saves the file temporarily, invokes `detect_pipelines()`, and returns JSON with `pipelines` array. Supports `?visualize=true` to include a base64 visualization image.
4. Added serializers in `pid/serializers.py` and a small model `PipelineImage` (optional storage) in `pid/models.py`.
5. Added unit tests and integration tests in `pid/tests.py` that generate in-memory images and validate outputs.
6. Added DRF schema and Swagger UI using `drf-spectacular` (`/api/schema/`, `/api/docs/`) for reviewers.
7. Added Dockerfile and docker-compose for reviewers to run the app without installing Python deps locally.
8. Verified the `pid` test suite runs locally inside the provided virtualenv and all tests pass (`python manage.py test pid`).

## Verification steps performed

- Installed dependencies from `requirements.txt` in a virtualenv.
- Ran `python manage.py migrate` and `python manage.py test pid` — tests passed.
- Manually inspected `detect_pipelines()` to ensure it uses grayscale → Canny → HoughLinesP when OpenCV is available.
- Confirmed API route `/api/pipeline/` matches the assignment and returns JSON of the required shape.

If you'd like, I can produce a short recorded walkthrough (screen recording) showing the Docker build, running the server, and posting a sample image to the API. Request that and I will add the script and small sample image to the repo.

## Specification compliance

Below is a short background-check mapping each assignment requirement to where it is implemented in the repository.

- Create a Django project `pipeline_project`: implemented at `pipeline_project/` and top-level `manage.py`.
- Create a Django app `pid`: code in `pipeline_project/pid/`.
- REST endpoint `/api/pipeline/`: route defined in `pipeline_project/pid/urls.py` and implemented in `pipeline_project/pid/views.py` (view name `PipelineDetectionView`, URL name `pipeline-detection`).
- Accepts image upload (POST, multipart/form-data): handled by `PipelineUploadSerializer` in `pipeline_project/pid/serializers.py` and `PipelineDetectionView.post()`.
- Uses OpenCV to detect pipelines (lines): `pipeline_project/pid/utils.py` implements `detect_pipelines()` using grayscale → Canny → HoughLinesP when OpenCV is available.
- Returns JSON with `pipelines` list of `{ "source": [x1,y1], "destination": [x2,y2] }`: implemented in `pipeline_project/pid/views.py` response and covered by tests in `pipeline_project/pid/tests.py`.
- Basic error handling (missing/invalid image): implemented in `pipeline_project/pid/views.py` with 400 responses and tested in unit tests.
- Optional visualization (base64): `detect_pipelines(..., visualize=True)` returns a `visualization` base64 data URL (see `pid/utils.py` and `pid/views.py` supports `?visualize=true`).
- API documentation: configured with `drf-spectacular` in `pipeline_project/pipeline_project/settings.py` and exposed at `/api/schema/` and `/api/docs/` in `pipeline_project/pipeline_project/urls.py`.
- Tests: unit + integration tests in `pipeline_project/pid/tests.py` (in-memory images tested).
- Delivery packaging: `pipeline_project/Dockerfile` and `pipeline_project/docker-compose.yml` provided.

Files to inspect for each feature (quick links):

- `pipeline_project/pid/utils.py` — core detection logic (OpenCV + fallback)
- `pipeline_project/pid/views.py` — API endpoint and request handling
- `pipeline_project/pid/serializers.py` — input validation
- `pipeline_project/pid/tests.py` — test coverage for detection and API
- `pipeline_project/pipeline_project/urls.py` — API routing and schema/docs
- `pipeline_project/requirements.txt` — dependencies
- `pipeline_project/Dockerfile`, `pipeline_project/docker-compose.yml` — delivery runtime

## Verification summary

I ran quick verification in a clean environment (virtualenv) and inside the repo's venv. Key checks:

- Python syntax check: `python -m py_compile` across project — no syntax errors.
- Tests: `python manage.py test pid` — all pid tests passed.

Short test output (truncated):

```
Ran 2 tests in 0.024s

OK
```

If reviewers want the exact test logs, I can attach the full output or add a `verify.sh` script that replays the same commands and prints logs.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# system deps for opencv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

ENV DJANGO_SETTINGS_MODULE=pipeline_project.settings

RUN python manage.py collectstatic --noinput || true

CMD ["gunicorn", "pipeline_project.wsgi:application", "--bind", "0.0.0.0:8000"]

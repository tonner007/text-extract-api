# Use an official Python runtime as a parent image
FROM python:3.10-slim

RUN echo 'Acquire::http::Pipeline-Depth 0;\nAcquire::http::No-Cache true;\nAcquire::BrokenProxy true;\n' > /etc/apt/apt.conf.d/99fixbadproxy

# Clear the APT cache, update package lists, and install dependencies
RUN apt-get clean && rm -rf /var/lib/apt/lists/* \
    && apt-get update --fix-missing \
    && apt-get install -y \
        libgl1-mesa-glx \
        tesseract-ocr \
        libtesseract-dev \
        poppler-utils \
        libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

## Copy main project file
#COPY pyproject.toml README.md LICENSE text_extract_api/ ./
#
## Install environment
#RUN pip install -e .
#
## Copy rest files
#COPY . .
#
#RUN python -c 'from marker.models import load_all_models; load_all_models()'

# Expose the port the FastAPI text_extract_api runs on
EXPOSE 8000

# Define the command to run your application
CMD ["uvicorn", "text_extract_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

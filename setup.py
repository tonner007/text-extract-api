from setuptools import setup, find_packages

setup(
    name='text_extract_api',
    version='0.1.0',
    packages=find_packages(),
    url='https://github.com/CatchTheTornado/text-extract-api',
    description='Images and documents (PDF, Word, PPTX ...) extraction and parse API using state of the art modern OCRs + Ollama supported models. Anonymize documents. Remove PII. Convert any document or picture to structured JSON or Markdown'
)

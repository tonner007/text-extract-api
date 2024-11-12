# pdf-extract-api

Convert any image or PDF to Markdown *text* or JSON structured document with super-high accuracy, including tabular data, numbers or math formulas.

The API is built with FastAPI and uses Celery for asynchronous task processing. Redis is used for caching OCR results.

![hero doc extract](ocr-hero.webp)

## Features:
- **No Cloud/external dependencies** all you need: PyTorch based OCR (Marker) + Ollama are shipped and configured via `docker-compose` no data is sent outside your dev/server environment,
- **PDF to Markdown** conversion with very high accuracy using different OCR strategies including [marker](https://github.com/VikParuchuri/marker), [surya-ocr](https://github.com/VikParuchuri/surya) or [tessereact](https://github.com/h/pytesseract)
- **PDF to JSON** conversion using Ollama supported models (eg. LLama 3.1)
- **LLM Improving OCR results** LLama is pretty good with fixing spelling and text issues in the OCR text
- **Removing PII** This tool can be used for removing Personally Identifiable Information out of PDF - see `examples`
- **Distributed queue processing** using [Celery][(](https://docs.celeryq.dev/en/stable/getting-started/introduction.html))
- **Caching** using Redis - the OCR results can be easily cached prior to LLM processing
- **CLI tool** for sending tasks and processing results 

## Screenshots

Converting MRI report to Markdown + JSON.

```bash 
python client/cli.py ocr --file examples/example-mri.pdf --prompt_file examples/example-mri-2-json-prompt.txt
```

Before running the example see [getting started](#getting-started)

![Converting MRI report to Markdown](./screenshots/example-1.png)

Converting Invoice to JSON and remove PII

```bash 
python client/cli.py ocr --file examples/example-invoice.pdf --prompt_file examples/example-invoice-remove-pii.txt 
```

Before running the example see [getting started](#getting-started)

![Converting Invoice to JSON](./screenshots/example-2.png)

**Note:** As you may observe in the example above, `marker-pdf` sometimes mismatches the cols and rows which could have potentially great impact on data accuracy. To improve on it there is a feature request [#3](https://github.com/CatchTheTornado/pdf-extract-api/issues/3) for adding alternative support for [`tabled`](https://github.com/VikParuchuri/tabled) model - which is optimized for tables.

## Getting started

You might want to run the app directly on your machine for development purposes OR to use for example Apple GPUs (which are not supported by Docker at the moment).

To have it up and running please execute the following steps:

[Download and install Ollama](https://ollama.com/download)
[Download and install Docker](https://www.docker.com/products/docker-desktop/)

If you are on Mac or just need to have your dependencies well organized, create a [virtual python env](https://docs.python.org/3/library/venv.html):

```bash
python3 -m venv .venv
source .venv/bin/activate
# now you've got access to `python` and `pip` commands
```

Configure environment variables:

```bash
cp .env.localhost.example .env.localhost
```

You might want to just use the defaults - should be fine. After ENV variables are set, just execute:

```bash
chmod +x run.sh
run.sh
```

This command will install all the dependencies - including Redis (via Docker, so it is not entirely docker free method of running `pdf-extract-api` anyways :)

Then you're good to go with running some CLI commands like:

```bash
python client/cli.py ocr --file examples/example-mri.pdf --ocr_cache --prompt_file=examples/example-mri-remove-pii.txt
```

### Scalling the parallell processing

To have multiple tasks runing at once - for concurrent processing please run the following command to start single worker process:

```bash
celery -A main.celery worker --loglevel=info --pool=solo & # to scale by concurrent processing please run this line as many times as many concurrent processess you want to have running
```

## Getting started with Docker

### Prerequisites

- Docker
- Docker Compose

### Clone the Repository

```sh
git clone https://github.com/CatchTheTornado/pdf-extract-api.git
cd pdf-extract-api
```

### Setup environmental variables

Create `.env` file in the root directory and set the necessary environment variables. You can use the `.env.example` file as a template:

```bash
# defaults for docker instances
cp .env.example .env`
```

or 

```bash
# defaults for local run
cp .env.example.localhost .env
```

Then modify the variables inside the file:

```bash
#APP_ENV=production # sets the app into prod mode, othervise dev mode with auto-reload on code changes
REDIS_CACHE_URL=redis://localhost:6379/1

# CLI settings
OCR_URL=http://localhost:8000/ocr
RESULT_URL=http://localhost:8000/ocr/result/{task_id}
CLEAR_CACHE_URL=http://localhost:8000/ocr/clear_cach
LLM_PULL_API_URL=http://localhost:8000/llm_pull
LLM_GENEREATE_API_URL=http://localhost:8000/llm_generate

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
OLLAMA_HOST=http://localhost:11434
APP_ENV=development  # Default to development mode
```

### Build and Run the Docker Containers

Build and run the Docker containers using Docker Compose:

```bash
docker-compose up --build
```

... for GPU support run:

```bash
docker-compose -f docker-compose.gpu.yml up --build
```

**Note:** While on Mac - Docker does not support Apple GPUs. In this case you might want to run the application natively without the Docker Compose please check [how to run it natively with GPU support](#getting-started)


This will start the following services:
 - **FastAPI App**: Runs the FastAPI application.
 - **Celery Worker**: Processes asynchronous OCR tasks.
 - **Redis**: Caches OCR results.
 - **Ollama**: Runs the Ollama model.


## Hosted edition

If the on-prem is too much hassle [ask us about the hosted/cloud edition](mailto:info@catchthetornado.com?subject=pdf-extract-api%20but%20hosted) of pdf-extract-api, we can setup it you, billed just for the usage.

## CLI tool

**Note**: While on Mac, you may need to create a virtual Python environment first:

```bash
python3 -m venv .venv
source .venv/bin/activate
# now you've got access to `python` and `pip` within your virutal env.
pip install -r app/requirements.txt # install main project requirements
```


The project includes a CLI for interacting with the API. To make it work first run:

```bash
cd client
pip install -r requirements.txt
```


### Pull the LLama3.1 model

You might want to test out [different models supported by LLama](https://ollama.com/library)

```bash
python client/cli.py llm_pull --model llama3.1
```


### Upload a File for OCR (converting to Markdown)

```bash
python client/cli.py ocr --file examples/example-mri.pdf --ocr_cache
```


### Upload a File for OCR (processing by LLM)

**Important note:** To use LLM you must first run the **llm_pull** to get the specific model required by your requests.

For example you must run:

```bash
python client/cli.py llm_pull --model llama3.1
```

and only after to run this specific prompt query:

```bash
python client/cli.py ocr --file examples/example-mri.pdf --ocr_cache --prompt_file=examples/example-mri-remove-pii.txt
```

The `ocr` command can store the results using the `storage_profiles`:
  - **storage_profile**: Used to save the result - the `default` profile (`/storage_profiles/default.yaml`) is used by default; if empty file is not saved
  - **storage_filename**: Outputting filename - relative path of the `root_path` set in the storage profile - by default a relative path to `/storage` folder; can use placeholders for dynamic formatting: `{file_name}`, `{file_extension}`, `{Y}`, `{mm}`, `{dd}` - for date formatting, `{HH}`, `{MM}`, `{SS}` - for time formatting


### Upload a File for OCR (processing by LLM), store result on disk

```bash
python client/cli.py ocr --file examples/example-mri.pdf --ocr_cache --prompt_file=examples/example-mri-remove-pii.txt  --storage_filename "invoices/{Y}/{file_name}-{Y}-{mm}-{dd}.md"
```

### Get OCR Result by Task ID

```bash
python client/cli.py result --task_id {your_task_id_from_upload_step}
```

### List file results archived by `storage_profile`

```bash
python client/cli.py list_files 
```

to use specific (in this case `google drive`) storage profile run:

```bash
python client/cli.py list_files  --storage_profile gdrive
```

### Load file result archived by `storage_profile`

```bash
python client/cli.py load_file --file_name "invoices/2024/example-invoice-2024-10-31-16-33.md"
```

### Delete file result archived by `storage_profile`

```bash
python client/cli.py delete_file --file_name "invoices/2024/example-invoice-2024-10-31-16-33.md" --storage_profile gdrive
```

or for default profile (local file system):

```bash
python client/cli.py delete_file --file_name "invoices/2024/example-invoice-2024-10-31-16-33.md" 
```

### Clear OCR Cache

```bash
python client/cli.py clear_cache
```

### Test LLama

```bash
python llm_generate --prompt "Your prompt here"
```

## Endpoints

### OCR Endpoint
- **URL**: /ocr
- **Method**: POST
- **Parameters**:
  - **file**: PDF file to be processed.
  - **strategy**: OCR strategy to use (`marker` or `tesseract`).
  - **ocr_cache**: Whether to cache the OCR result (true or false).
  - **prompt**: When provided, will be used for Ollama processing the OCR result
  - **model**: When provided along with the prompt - this model will be used for LLM processing
  - **storage_profile**: Used to save the result - the `default` profile (`/storage_profiles/default.yaml`) is used by default; if empty file is not saved
  - **storage_filename**: Outputting filename - relative path of the `root_path` set in the storage profile - by default a relative path to `/storage` folder; can use placeholders for dynamic formatting: `{file_name}`, `{file_extension}`, `{Y}`, `{mm}`, `{dd}` - for date formatting, `{HH}`, `{MM}`, `{SS}` - for time formatting

Example:

```bash
curl -X POST -H "Content-Type: multipart/form-data" -F "file=@examples/example-mri.pdf" -F "strategy=marker" -F "ocr_cache=true" -F "prompt=" -F "model=" "http://localhost:8000/ocr" 
```

### OCR Result Endpoint
- **URL**: /ocr/result/{task_id}
- **Method**: GET
- **Parameters**:
  - **task_id**: Task ID returned by the OCR endpoint.

Example:

```bash
curl -X GET "http://localhost:8000/ocr/result/{task_id}"
```

### Clear OCR Cache Endpoint
 - **URL**: /ocr/clear_cache
 - **Method**: POST

Example:
```bash
curl -X POST "http://localhost:8000/ocr/clear_cache"
```


### Ollama Pull Endpoint
- **URL**: /llm/pull
- **Method**: POST
- **Parameters**:
  - **model**: Pull the model you are to use first

Example:

```bash
curl -X POST "http://localhost:8000/llama_pull" -H "Content-Type: application/json" -d '{"model": "llama3.1"}'
```

### Ollama Endpoint
- **URL**: /llm/generate
- **Method**: POST
- **Parameters**:
  - **prompt**: Prompt for the Ollama model.
  - **model**: Model you like to query

Example:

```bash
curl -X POST "http://localhost:8000/llama_generate" -H "Content-Type: application/json" -d '{"prompt": "Your prompt here", "model":"llama3.1"}'
```

### List storage files:
 
- **URL:** /storage/list
- **Method:** GET
- **Parameters**:
  - **storage_profile**: Name of the storage profile to use for listing files (default: `default`).

### Download storage file:
 
- **URL:** /storage/load
- **Method:** GET
- **Parameters**:
  - **file_name**: File name to load from the storage
  - **storage_profile**: Name of the storage profile to use for listing files (default: `default`).

### Delete storage file:
 
- **URL:** /storage/delete
- **Method:** DELETE
- **Parameters**:
  - **file_name**: File name to load from the storage
  - **storage_profile**: Name of the storage profile to use for listing files (default: `default`).


## Storage profiles

The tool can automatically save the results using different storage strategies and storage profiles. Storage profiles are set in the `/storage_profiles` by a yaml configuration files.

Example:

```yaml
strategy: local_filesystem
settings:
  root_path: /storage # The root path where the files will be stored - mount a proper folder in the docker file to match it
  subfolder_names_format: "" # eg: by_months/{Y}-{mm}/
  create_subfolders: true
```

for Google drive:

```yaml
strategy: google_drive
settings:
## how to enable GDrive API: https://developers.google.com/drive/api/quickstart/python?hl=pl

  service_account_file: /storage/client_secret_269403342997-290pbjjlb06nbof78sjaj7qrqeakp3t0.apps.googleusercontent.com.json
  folder_id:
```

Where the `service_account_file` is a `json` file with authorization credentials. Please read on how to enable Google Drive API and prepare this authorization file [here](https://developers.google.com/drive/api/quickstart/python?hl=pl).

Note: Service Account is different account that the one you're using for Google workspace (files will not be visible in the UI)

## License
This project is licensed under the GNU General Public License. See the [LICENSE](LICENSE.md) file for details.

**Important note on [marker](https://github.com/VikParuchuri/marker) license***:

The weights for the models are licensed `cc-by-nc-sa-4.0`, but Marker's author will waive that for any organization under $5M USD in gross revenue in the most recent 12-month period AND under $5M in lifetime VC/angel funding raised. You also must not be competitive with the [Datalab API](https://www.datalab.to/). If you want to remove the GPL license requirements (dual-license) and/or use the weights commercially over the revenue limit, check out the options [here](https://www.datalab.to/).



## Contact
In case of any questions please contact us at: info@catchthetornado.com

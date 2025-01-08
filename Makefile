SHELL := /bin/bash

.PHONY: help install run-server start-workers build-docker test clean pull-models scale-workers clear-cache logs list-files delete-file

# @ChoSH group setup;32;Setup commands
# @ChoSH group build;34;"Build commands
# @ChoSH group run;36;Run and execution commands
# @ChoSH group test;33;Test commands
# @ChoSH group debug;35;Debugging commands
# @ChoSH group clean;31;Cleanup commands

.PHONY: listShort
listShort:
	grep '^# @ChoSH group' $(MAKEFILE_LIST) | while IFS= read -r line; do \
	    params=$$(echo $$line | sed 's/^# @ChoSH group //'); \
	    IFS=";" read -r name color label <<< "$$params"; \
	    desc=$$(echo $$desc | sed 's/^"\(.*\)"$$/\1/'); \
	    echo "$$name | $$color | $$label"; \
	done
	@$(call chomh_read_short,$(process_block))

# Displays a list of commands and their descriptions
help:
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?#"} /^[a-zA-Z_-]+:.*?#/ {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

install:  # Installation of dependencies and preparation of virtual environment
	python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

run-server:  # Starting the local application server
	chmod +x run.sh && ./run.sh

start-workers:  # Starting Celery workers
	celery -A main.celery worker --loglevel=info --pool=solo

build-docker:  # Building and starting Docker containers
	docker-compose up --build

test:  # Running unit testsyes
	pytest

clean:  # Removing the virtual environment and stopping Docker
	rm -rf .venv && docker-compose down -v

pull-models:  # Downloading LLama models
	python client/cli.py llm_pull --model llama3.1
	python client/cli.py llm_pull --model llama3.2-vision

scale-workers:  # Scaling Celery workers for parallel processing
	celery -A main.celery worker --loglevel=info --concurrency=4

clear-cache:  # Clearing OCR cache
	python client/cli.py clear_cache

logs:  # Retrieving logs from the Docker application
	docker-compose logs -f

list-files:  # Listing files stored in storage
	python client/cli.py list_files

delete-file:  # Deleting a specific file from storage
	@read -p "Give filename to delete " filename; \
	python client/cli.py delete_file --file_name $$filename

process_block = \
    echo "block $$2 of type $$1 has description $$3"

chomh_read_short = \
	grep '^# @ChoSH group' $(MAKEFILE_LIST) | while IFS= read -r line; do \
	    params=$$(echo $$line | sed 's/^# @ChoSH group //'); \
	    IFS=';' read -r name color label <<< "$$params"; \
	    desc=$$(echo $$desc | sed 's/^"\(.*\)"$$/\1/'); \
	    echo "$$name | $$color | $$label"; \
	done

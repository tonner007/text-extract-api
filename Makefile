SHELL := /bin/bash

.PHONY: help install install-linux install-macos install-requirements start-local-server setup-docker run-docker run-docker-gpu clean clear-cache

help:
	@echo "Available commands:"
	@echo " make install (recommended)   - Automatic setup for local or Docker"
	@echo " make start-local-server      - Start the local application server"
	@echo " setup-docker                - Setup Docker environment"
	@echo " run-docker                  - Run Docker containers with CPU support"
	@echo " run-docker-gpu              - Run Docker containers with GPU support"
	@echo " clean                       - Clean the project environment"
	@echo " clear-cache                 - Clear application cache"

install:
	@width=$$(tput cols || echo 100); \
	[ "$$width" -gt "100" ] && width=100; \
	padding=$$(printf "%$${width}s" "" | tr ' ' '#'); \
	printf "\n\e[1;34m%s\e[0m\n" "$$padding"; \
	printf "\e[1;34m###%*sCatchTheTornado/text-extract-api%*s###\e[0m\n" $$(($$width / 2 - 21)) "" $$(($$width / 2 - 17)) ""; \
	printf "\e[1;34m###%*sAUTOMATIC SETUP%*s###\e[0m\n" $$(($$width / 2 - 10)) "" $$(($$width / 2 - 11)) ""; \
	printf "%s\n" "$$padding"; \
	printf "\e[1;34m   Do you want to run the application locally or with Docker?\e[0m\n"; \
	printf "\e[1;33m   [L] \e[0m Local - Run the application locally\n"; \
	printf "\e[1;33m   [D] \e[0m Docker - Run the axpplication in Docker\n"; \
	read -p "   > " choice; \
	case "$$choice" in \
		[lL]) echo -e "\033[1;32m   ✔ You chose: Local Setup\033[0m"; $(MAKE) setup-local ;; \
		[dD]) echo -e "\033[1;32m   ✔ You chose: Docker\033[0m"; $(MAKE) setup-docker ;; \
		*) echo "Invalid option. Exiting."; exit 1 ;; \
	esac

setup-local:
	@while true; do \
		printf  "\n\e[1;34m   Python setup environment...\e[0m"; \
		python3 -m venv .venv && source .venv/bin/activate; \
		printf "\e[1;34m\n   Do you want to install requirements?\e[0m\n"; \
		printf "\e[1;33m   [y] \e[0m Yes - Install and then run application locally\n"; \
		printf "\e[1;33m   [n] \e[0m No  - Skip and run application locally \n"; \
	read -p "   > " choice; \
		case "$$choice" in \
			[yY]) \
				echo -e "\033[1;32m   ✔ Installing Python dependencies...\033[0m"; \
				$(MAKE) install-requirements; \
				break; \
				;; \
			[nN]|[sS]) \
				echo -e "\033[1;33m   Skipping requirement installation. Starting the local server instead...\033[0m"; \
				$(MAKE) start-local-server; \
				break; \
				;; \
			*) \
				echo -e "\033[1;31m   Invalid input: Please enter 'y', 'n', or 's' to proceed.\033[0m"; \
				;; \
		esac; \
	done


install-linux:
	@echo -e "\033[1;34m   Installing Linux dependencies...\033[0m"; \
	sudo apt update && sudo apt install -y libmagic1 tesseract-ocr poppler-utils pkg-config

install-macos:
	@echo -e "\033[1;34m   Installing macOS dependencies...\033[0m"; \
	brew update && brew install libmagic tesseract poppler pkg-config ghostscript ffmpeg automake autoconf

install-requirements:
	@if [ "$$(uname)" = "Linux" ]; then $(MAKE) install-linux; \
	elif [ "$$(uname)" = "Darwin" ]; then $(MAKE) install-macos; \
	else echo "Unsupported OS. Exiting."; exit 1; fi; \
	pip install -r app/requirements.txt

start-local-server:
	@echo "Starting the local application server..."; \
	./run.sh

setup-docker:
	@echo -e "\033[1;34m   Available Docker options:\033[0m"; \
	echo -e "\033[1;33m     1:\033[0m Run Docker containers with CPU support"; \
	echo -e "\033[1;33m     2:\033[0m Run Docker containers with GPU support"; \
	read -p "Enter your choice (1 = CPU, 2 = GPU, any other key to exit): " docker_choice; \
	case "$$docker_choice" in \
		1) $(MAKE) run-docker ;; \
		2) $(MAKE) run-docker-gpu ;; \
		*) echo -e "\033[1;34m   Exiting without starting Docker.\033[0m" ;; \
	esac

run-docker:
	@echo -e "\033[1;34m   Starting Docker container with CPU support...\033[0m"; \
	docker-compose up --build

run-docker-gpu:
	@echo -e "\033[1;34m   Starting Docker container with GPU support...\033[0m"; \
	docker-compose -f docker-compose.gpu.yml up --build

clean:
	@echo "Cleaning project..."; \
	rm -rf .venv; \
	docker-compose down -v; \
	$(MAKE) clean-cache

clean-cache:
	find . -type d -name '__pycache__' -exec rm -rf {} + && find . -type f -name '*.pyc' -delete

clear-cache:
	python client/cli.py clear_cache

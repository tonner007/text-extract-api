import argparse
import requests
import time
import os

def upload_file(file_path, ocr_cache):
    ocr_url = os.getenv('OCR_URL', 'http://localhost:8000/ocr')
    files = {'file': open(file_path, 'rb')}
    data = {'ocr_cache': ocr_cache}
    response = requests.post(ocr_url, files=files, data=data)
    if response.status_code == 200:
        respObject = response.json()
        if respObject.get('task_id'):
            return {
                        "task_id": respObject.get('task_id')
            }
        else:
            return {
                        "text": respObject.get('text')
            }
    else:
        print(f"Failed to upload file: {response.text}")
        return None

def get_result(task_id):
    result_url = os.getenv('RESULT_URL', f'http://localhost:8000/ocr/result/{task_id}')
    while True:
        response = requests.get(result_url)
        if response.status_code == 200:
            result = response.json()
            if result['state'] == 'SUCCESS':
                return result['result']
            elif result['state'] == 'FAILURE':
                print("OCR task failed.")
                return None
        time.sleep(2)  # Wait for 2 seconds before checking again

def clear_cache():
    clear_cache_url = os.getenv('CLEAR_CACHE_URL', 'http://localhost:8000/ocr/clear_cache')
    response = requests.post(clear_cache_url)
    if response.status_code == 200:
        print("OCR cache cleared successfully.")
    else:
        print(f"Failed to clear OCR cache: {response.text}")

def run_ollama(prompt):
    ollama_url = os.getenv('OLLAMA_API_URL', 'http://localhost:8000/llama_test')
    response = requests.post(ollama_url, json={"model": "llama-3.1", "prompt": prompt})
    if response.status_code == 200:
        print("Ollama Result:")
        print(response.json())
    else:
        print(f"Failed to generate text: {response.text}")

def main():
    parser = argparse.ArgumentParser(description="CLI for OCR and Ollama operations.")
    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')

    # Sub-command for uploading a file
    upload_parser = subparsers.add_parser('upload', help='Upload a file to the OCR endpoint and get the result.')
    upload_parser.add_argument('--file', type=str, default='examples/rmi-example.pdf', help='Path to the file to upload')
    upload_parser.add_argument('--ocr_cache', action='store_true', help='Enable OCR result caching')

    # Sub-command for getting the result
    upload_parser = subparsers.add_parser('result', help='Get the OCR result by specified task id.')
    upload_parser.add_argument('--task_id', type=str, help='Task Id returned by the upload command')


    # Sub-command for clearing the cache
    clear_cache_parser = subparsers.add_parser('clear_cache', help='Clear the OCR result cache')

    # Sub-command for running Ollama
    ollama_parser = subparsers.add_parser('ollama', help='Run the Ollama endpoint')
    ollama_parser.add_argument('--prompt', type=str, required=True, help='Prompt for the Ollama model')

    args = parser.parse_args()

    if args.command == 'upload':
        result = upload_file(args.file, args.ocr_cache)
        if result.get('text'):
            print("OCR Result:")
            print(result.get('text'))
        elif result:
            print("File uploaded successfully. Task Id: " + result.get('task_id') +  " Waiting for the result...")
            text_result = get_result(result.get('task_id'))
            if text_result:
                print("OCR Result:")
                print(text_result)
    elif args.command == 'result':
        text_result = get_result(args.task_id)
        if text_result:
            print("OCR Result:")
            print(text_result)
    elif args.command == 'clear_cache':
        clear_cache()
    elif args.command == 'ollama':
        run_ollama(args.prompt)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
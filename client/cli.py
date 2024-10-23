import argparse
import requests
import time
import os

def upload_file(file_path):
    ocr_url = os.getenv('OCR_URL', 'http://localhost:8000/ocr')
    files = {'file': open(file_path, 'rb')}
    response = requests.post(ocr_url, files=files)
    if response.status_code == 200:
        return response.json()['task_id']
    else:
        print(f"Failed to upload file: {response.text}")
        return None

def get_result(task_id):
    result_url = os.getenv('RESULT_URL', f'http://localhost:8000/ocr/result/{task_id}')
    while True:
        response = requests.get(result_url)
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'completed':
                return result['text']
            elif result['status'] == 'failed':
                print("OCR task failed.")
                return None
        time.sleep(2)  # Wait for 2 seconds before checking again

def main():
    parser = argparse.ArgumentParser(description="Upload a file to the OCR endpoint and get the result.")
    parser.add_argument('--file', type=str, default='examples/example-mri.pdf', help='Path to the file to upload')
    args = parser.parse_args()

    task_id = upload_file(args.file)
    if task_id:
        print("File uploaded successfully. Waiting for the result...")
        text_result = get_result(task_id)
        if text_result:
            print("OCR Result:")
            print(text_result)

if __name__ == "__main__":
    main()
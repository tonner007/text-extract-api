import boto3
import os
from string import Template
from botocore.exceptions import NoCredentialsError, ClientError
from storage_strategies.storage_strategy import StorageStrategy

class AWSS3StorageStrategy(StorageStrategy):
    def __init__(self, context):
        super().__init__(context)

        self.bucket_name = self._resolve_placeholder(context['settings'].get('bucket_name'))
        self.region = self._resolve_placeholder(context['settings'].get('region'))
        self.access_key = self._resolve_placeholder(context['settings'].get('access_key'))
        self.secret_access_key = self._resolve_placeholder(context['settings'].get('secret_access_key'))

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region
        )

    def _resolve_placeholder(self, value):
        if not value:
            return None
        return Template(value).substitute(os.environ)

    def save(self, file_name, dest_file_name, content):
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=dest_file_name,
                Body=content.encode('utf-8')
            )
            print(f"File {dest_file_name} saved to S3 bucket {self.bucket_name}.")
        except NoCredentialsError:
            print("AWS credentials are missing or invalid.")
        except ClientError as e:
            print(f"Failed to upload {file_name}: {e}")

    def load(self, file_name):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_name)
            return response['Body'].read().decode('utf-8')
        except ClientError as e:
            print(f"Failed to download {file_name}: {e}")
            return None

    def list(self):
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            return [item['Key'] for item in response.get('Contents', [])]
        except ClientError as e:
            print(f"Failed to list files: {e}")
            return []

    def delete(self, file_name):
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_name)
            print(f"File {file_name} deleted from S3 bucket {self.bucket_name}.")
        except ClientError as e:
            print(f"Failed to delete {file_name}: {e}")

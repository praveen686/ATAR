from google.cloud import storage


class SECDataManager:
    SEC_URL = "https://www.sec.gov/path/to/companyfacts.zip"
    BUCKET_NAME = "your_gcs_bucket_name"
    FILE_NAME = "companyfacts.zip"

    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.BUCKET_NAME)

    def download_and_replace(self):
        response = requests.get(self.SEC_URL, stream=True)

        blob = self.bucket.blob(self.FILE_NAME)
        blob.upload_from_file(response.raw, content_type='application/zip')

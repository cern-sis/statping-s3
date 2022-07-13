# Statping <=> S3 Sync

This a CLI tool to sync statping data with S3.

## Requirements

1. Python 3

## Installation

1. Create a virtual enviornment - `python3 -m venv env`

2. Start the virtual env - `source env/bin/activate`

3. Install dependencies - `pip install -r requirements.txt`

## Usage

The tools has two commands listed below. 

The arguments required are:

1. File Name - File name to fetch/save in S3 bucket.
2. Bucket Name - Bucket name to fetch/save the statping data.
3. Access Key - AWS S3 client access key
4. Secret Key - AWS S3 client secret key
5. S3 Host - Host URL of the S3 Instance
6. Host URL - URL of the statping import/export API endpoint. For example: `http://localhost:8080/api/settings/[export/import]`
7. Token - Auth Token to access the statping API

### Export Services

- `python statping.py export-services <file_name> <bucket_name> <access_key> <secret_key> <s3_host> <host_url> <token>`

### Import Services

- `python statping.py create-services <file_name> <bucket_name> <access_key> <secret_key> <s3_host> <host_url> <token>`


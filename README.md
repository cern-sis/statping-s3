# Statping <=> S3 Sync

This a CLI tool to sync statping data with S3.

## Requirements

1. Python 3

## Installation

1. Create a virtual enviornment - `python3 -m venv env`

2. Start the virtual env - `source env/bin/activate`

3. Install dependencies - `pip install -r requirements.txt`

## Usage

The tools has two scripts. 

The required enviornment variables are:

1. File Name - File name to fetch/save in S3 bucket.
2. Bucket Name - Bucket name to fetch/save the statping data.
3. S3 Access Key - AWS S3 client access key
4. S3 Secret Key - AWS S3 client secret key
5. S3 Host - Host URL of the S3 Instance
6. Statping Host URL - URL of the statping import/export API endpoint. For example: `http://localhost:8080/api/settings/[export/import]`
7. Statping API Token - Auth Token to access the statping API
8. Customer Master Key Description - CMK key description

### Export Services

- `./export-services.py`

### Import Services

- `./import-services.py`

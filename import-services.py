#!/usr/bin/env python
import json
import logging
import os

import boto3
import requests
from cryptography.fernet import Fernet


def create_services():
    """Import JSON data to Statping."""

    # Load env
    filename = os.environ["FILE_NAME"]
    bucketname = os.environ["BUCKET_NAME"]
    s3_access_key = os.environ["S3_ACCESS_KEY"]
    s3_secret_key = os.environ["S3_SECRET_KEY"]
    s3_host = os.environ["S3_HOST"]
    statping_host_url = os.environ["STATPING_HOST_URL"]
    statping_api_token = os.environ["API_SECRET"]
    encryption_key = os.environ["STATPING_DATA_KEY"]

    # Get the encrypted file from S3
    statping_services = None
    s3 = boto3.client(
        "s3",
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        endpoint_url=s3_host,
    )
    try:
        s3_response = s3.get_object(Bucket=bucketname, Key=filename)
        statping_services = s3_response["Body"].read()
        with open(filename, "wb") as file:
            file.write(statping_services)
    except Exception as e:
        logging.info("{} occured while fetching S3 bucket.".format(e))

    # Decrypt the services and update the monitoring dashboard
    if statping_services:
        f = Fernet(encryption_key)
        with open(filename, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data)
        obj = json.loads(decrypted_data)
        headers = {"Authorization": "Bearer {}".format(statping_api_token)}
        try:
            response = requests.post(statping_host_url, headers=headers, json=obj)
            if response.status_code == 200:
                logging.info("Statping service exported and uploaded successfully.")
            else:
                logging.info("{}".format(response.text))
        except Exception as e:
            logging.info("{} occured while craeting the statping service.".format(e))


if __name__ == "__main__":
    create_services()

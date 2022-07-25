#!/usr/bin/env python

import json
import logging
import os

import boto3
import requests
from cryptography.fernet import Fernet


def export_services():
    """Export Statping JSON data to S3."""

    # Load env
    filename = os.environ["FILE_NAME"]
    bucketname = os.environ["BUCKET_NAME"]
    s3_access_key = os.environ["S3_ACCESS_KEY"]
    s3_secret_key = os.environ["S3_SECRET_KEY"]
    s3_host = os.environ["S3_HOST"]
    statping_host_url = os.environ["STATPING_HOST_URL"]
    statping_api_token = os.environ["API_SECRET"]
    encryption_key = os.environ["STATPING_DATA_KEY"]

    # Export Statping services JSON
    try:
        response = requests.get(
            statping_host_url,
            headers={"Authorization": "Bearer {}".format(statping_api_token)},
        )
        services_json = response.json()
        if response.status_code == 200:
            with open(filename, "w") as file:
                json.dump(services_json, file)
        else:
            logging.error(
                "{} occured while exporting services.".format(response.status_code)
            )
    except Exception as e:
        logging.error("{} occured while exporting services.".format(e))

    # Encrypt the services and Upload to S3
    if encryption_key is None:
        logging.error("Encryption key not available.")

    f = Fernet(encryption_key)
    with open(filename, "rb") as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    with open(filename, "wb") as file:
        file.write(encrypted_data)
    logging.info("File encrypted successfully.")

    object_name = os.path.basename(filename)
    s3 = boto3.client(
        "s3",
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        endpoint_url=s3_host,
    )
    try:
        s3.upload_file(filename, bucketname, object_name)
        logging.info("Statping services exported and uploaded successfully.")
    except Exception as e:
        logging.info("{} occured while uploading file to S3.".format(e))

    return


if __name__ == "__main__":
    export_services()

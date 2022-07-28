#!/usr/bin/env python
import json
import logging
import os
import sys

from time import sleep

import boto3
import requests
from cryptography.fernet import Fernet


def import_services():
    """Import JSON data to Statping."""

    # Load env
    filename = os.environ["FILE_NAME"]
    bucketname = os.environ["BUCKET_NAME"]
    s3_access_key = os.environ["S3_ACCESS_KEY"]
    s3_secret_key = os.environ["S3_SECRET_KEY"]
    s3_host = os.environ["S3_HOST"]
    statping_export_host_url = os.environ["STATPING_HOST_EXPORT_URL"]
    statping_import_host_url = os.environ["STATPING_HOST_IMPORT_URL"]
    statping_api_token = os.environ["API_SECRET"]
    encryption_key = os.environ["STATPING_DATA_KEY"]

    # Check services and import only if no services are present
    logging.info("Starting Logging")
    headers = {"Authorization": "Bearer {}".format(statping_api_token)}
    """
    try:
        logging.info("Sleeping for 30 seconds")
        sleep(30)
        response = requests.get(
            statping_export_host_url,
            headers=headers,
        )
        logging.info(response.status_code)
        if response.status_code == 200:
            logging.info("Export Hit")
            services_json = response.json()
            if services_json.get("services"):
                logging.info("Services already imported!")
                return
    except Exception as e:
        logging.error("{} occured while exporting services.".format(e))
    """
    # Get the encrypted file from S3
    logging.info("connect with s3")
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

    if statping_services:
        logging.info("waiting for statping to start")
        # Decrypt the services and update the monitoring dashboard
        f = Fernet(encryption_key)
        with open(filename, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data)
        obj = json.loads(decrypted_data)
        obj["users"] = []
        # Flag to check and retry the import
        retry = 3
        while retry > 0:
            logging.info(retry)
            if retry == 3:
                sleep(35)
            try:
                retry -= 1
                response = requests.post(
                    statping_import_host_url, headers=headers, json=obj
                )
                logging.info(response.status_code)
                if response.status_code == 200:
                    logging.info("Statping service exported and uploaded successfully.")
                    break
            except Exception as e:
                logging.info(
                    "{} occured while creating the statping service.".format(e)
                )
            sleep(5)

        if retry == 0:
            logging.info(
                "Maximum retries exceeded, Please check the logs and try again."
            )
    return


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    import_services()

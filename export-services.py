#!/usr/bin/env python

import json
import logging
import os

import boto3
import requests


def load_env():
    return (
        os.environ["FILE_NAME"],
        os.environ["BUCKET_NAME"],
        os.environ["S3_ACCESS_KEY"],
        os.environ["S3_SECRET_KEY"],
        os.environ["S3_HOST"],
        os.environ["STATPING_HOST_URL"],
        os.environ["STATPING_API_TOKEN"],
    )


def export_services():
    file_name, bucket_name, access_key, secret_key, s3_host, host_url, token = load_env
    try:
        response = requests.get(
            host_url, headers={"Authorization": "Bearer {}".format(token)}
        )
        services_json = response.json()
        json.dump(services_json, file_name)
    except Exception as e:
        logging.info("{} occured while exporting services.".format(e))

    object_name = os.path.basename(file_name)
    s3 = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=s3_host,
    )
    try:
        s3.upload_file(file_name, bucket_name, object_name)
        logging.info("Statping services exported and uploaded successfully.")
    except Exception as e:
        logging.info("{} occured while uploading file to S3.".format(e))


if __name__ == "__main__":
    export_services()

#!/usr/bin/env python

import base64
import json
import logging
import os

import boto3
import requests
from cryptography.fernet import Fernet

NUM_BYTES_FOR_LEN = 4


def create_cmk(description):
    """Creates a KMS Customer Master Key

    Description is used to differentiate between CMKs.
    """

    kms_client = boto3.client("kms")
    response = kms_client.create_key(Description=description)

    # Return the key ID and ARN
    return response["KeyMetadata"]["KeyId"], response["KeyMetadata"]["Arn"]


def create_data_key(cmk_id, key_spec="AES_256"):
    """Generate a data key to use when encrypting and decrypting data"""

    # Create data key
    kms_client = boto3.client("kms")
    response = kms_client.generate_data_key(KeyId=cmk_id, KeySpec=key_spec)

    # Return the encrypted and plaintext data key
    return response["CiphertextBlob"], base64.b64encode(response["Plaintext"])


def encrypt_file(filename, cmk_id):
    """Encrypt JSON data using an AWS KMS CMK"""
    with open(filename, "rb") as file:
        file_contents = file.read()

    data_key_encrypted, data_key_plaintext = create_data_key(cmk_id)
    if data_key_encrypted is None:
        logging.error("Encryption key not available.")

    # Encrypt the data
    f = Fernet(data_key_plaintext)
    file_contents_encrypted = f.encrypt(file_contents)

    # Write the encrypted data key and encrypted file contents together
    with open(filename, "wb") as file_encrypted:
        file_encrypted.write(
            len(data_key_encrypted).to_bytes(NUM_BYTES_FOR_LEN, byteorder="big")
        )
        file_encrypted.write(data_key_encrypted)
        file_encrypted.write(file_contents_encrypted)
    logging.info("File encrypted successfully.")

    return


def export_services():
    """Export Statping JSON data to S3."""

    # Load env
    filename = os.environ["FILE_NAME"]
    bucketname = os.environ["BUCKET_NAME"]
    s3_access_key = os.environ["S3_ACCESS_KEY"]
    s3_secret_key = os.environ["S3_SECRET_KEY"]
    s3_host = os.environ["S3_HOST"]
    statping_host_url = os.environ["STATPING_HOST_URL"]
    statping_api_token = os.environ["STATPING_API_TOKEN"]
    cmk_description = os.environ["CMK_DESCRIPTION"]

    # Export Statping services JSON
    try:
        response = requests.get(
            statping_host_url,
            headers={"Authorization": "Bearer {}".format(statping_api_token)},
        )
        services_json = response.json()
        json.dump(services_json, filename)
    except Exception as e:
        logging.info("{} occured while exporting services.".format(e))

    # Encrypt and Upload to S3
    cmk_id, _ = create_cmk(cmk_description)
    encrypt_file(filename, cmk_id)
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

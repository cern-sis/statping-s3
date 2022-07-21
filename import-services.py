#!/usr/bin/env python

import base64
import json
import logging
import os

import boto3
import requests
from cryptography.fernet import Fernet

NUM_BYTES_FOR_LEN = 4


def decrypt_data_key(data_key_encrypted):
    """Decrypt an encrypted data key"""

    # Decrypt the data key
    kms_client = boto3.client("kms")
    response = kms_client.decrypt(CiphertextBlob=data_key_encrypted)

    # Return plaintext base64-encoded binary data key
    return base64.b64encode((response["Plaintext"]))


def decrypt_file(filename):
    """Decrypt a file encrypted by encrypt_file()"""

    # Read the encrypted file into memory
    with open(filename + ".encrypted", "rb") as file:
        file_contents = file.read()

    # The first NUM_BYTES_FOR_LEN tells us the length of the encrypted data key
    # Bytes after that represent the encrypted file data
    data_key_encrypted_len = (
        int.from_bytes(file_contents[:NUM_BYTES_FOR_LEN], byteorder="big")
        + NUM_BYTES_FOR_LEN
    )
    data_key_encrypted = file_contents[NUM_BYTES_FOR_LEN:data_key_encrypted_len]

    # Decrypt the data key before using it
    data_key_plaintext = decrypt_data_key(data_key_encrypted)
    if data_key_plaintext is None:
        return False

    # Decrypt the rest of the file
    f = Fernet(data_key_plaintext)
    file_contents_decrypted = f.decrypt(file_contents[data_key_encrypted_len:])

    # Write the decrypted file contents
    with open(filename, "wb") as file_decrypted:
        file_decrypted.write(file_contents_decrypted)


def create_services():
    """Import JSON data to Statping."""

    # Load env
    filename = os.environ["FILE_NAME"]
    bucketname = os.environ["BUCKET_NAME"]
    s3_access_key = os.environ["S3_ACCESS_KEY"]
    s3_secret_key = os.environ["S3_SECRET_KEY"]
    s3_host = os.environ["S3_HOST"]
    statping_host_url = os.environ["STATPING_HOST_URL"]
    statping_api_token = os.environ["STATPING_API_TOKEN"]

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
        statping_services = s3_response["Body"].read().decode("utf-8")
        json.dump(statping_services, filename)
    except Exception as e:
        logging.info("{} occured while fetching S3 bucket.".format(e))

    # Decrypt the services and update the monitoring dashboard
    if statping_services:
        decrypt_file(filename)
        with open(filename, "rb") as file_decrypted:
            obj = json.load(file_decrypted)
        headers = {"Authorization": "Bearer {}".format(statping_api_token)}
        try:
            response = requests.post(statping_host_url, headers=headers, json=obj)
            if response.status_code == 200:
                logging.info("Statping service exported and uploaded successfully.")
            else:
                logging.info("{}".format(response.json["error"]))
        except Exception as e:
            logging.info("{} occured while craeting the statping service.".format(e))


if __name__ == "__main__":
    create_services()

import json
import os

import boto3
import click
import requests


@click.group()
def statping():
    pass


@click.command()
@click.argument("file_name", type=click.File("w"))
@click.argument("bucket_name", type=click.STRING)
@click.argument("access_key", type=click.STRING)
@click.argument("secret_key", type=click.STRING)
@click.argument("s3_host", type=click.STRING)
@click.argument("host_url", type=click.STRING)
@click.argument("token", type=click.STRING)
def export_services(
    file_name, bucket_name, access_key, secret_key, s3_host, host_url, token
):
    try:
        response = requests.get(
            host_url, headers={"Authorization": "Bearer {}".format(token)}
        )
        services_json = response.json()
        json.dump(services_json, file_name)
    except Exception as e:
        click.echo("{} occured while exporting services.".format(e))

    object_name = os.path.basename(file_name)
    s3 = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=s3_host,
    )
    try:
        s3.upload_file(file_name, bucket_name, object_name)
        click.echo("Statping services exported and uploaded successfully.")
    except Exception as e:
        click.echo("{} occured while uploading file to S3.".format(e))


@click.command()
@click.argument("file_name", type=click.STRING)
@click.argument("bucket_name", type=click.STRING)
@click.argument("access_key", type=click.STRING)
@click.argument("secret_key", type=click.STRING)
@click.argument("s3_host", type=click.STRING)
@click.argument("host_url", type=click.STRING)
@click.argument("token", type=click.STRING)
def create_services(
    file_name, bucket_name, access_key, secret_key, s3_host, host_url, token
):
    statping_services = None
    s3 = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=s3_host,
    )
    try:
        s3_response = s3.get_object(Bucket=bucket_name, Key=file_name)
        statping_services = s3_response["Body"].read().decode("utf-8")
    except Exception as e:
        click.echo("{} occured while fetching S3 bucket.".format(e))

    if statping_services:
        obj = json.loads(statping_services)
        headers = {"Authorization": "Bearer {}".format(token)}
        try:
            response = requests.post(host_url, headers=headers, json=obj)
            if response.status_code == 200:
                click.echo("Statping service exported and uploaded successfully.")
            else:
                click.echo("{}".format(response.json["error"]))
        except Exception as e:
            click.echo("{} occured while craeting the statping service.".format(e))


statping.add_command(export_services)
statping.add_command(create_services)


if __name__ == "__main__":
    statping()

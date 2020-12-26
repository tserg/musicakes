import os
import json
from dotenv import load_dotenv

import boto3
from botocore.exceptions import ClientError

load_dotenv()

# Environment variables for AWS S3

S3_BUCKET = os.getenv('S3_BUCKET', 'Does not exist')
S3_KEY = os.getenv('S3_KEY', 'Does not exist')
S3_SECRET = os.getenv('S3_SECRET', 'Does not exist')
S3_LOCATION = os.getenv('S3_LOCATION', 'Does not exist')

def upload_file(file, key):
    """Upload a user's profile picture to an S3 bucket with public access

    :param file: File to upload
    :param key: Path name for the file
    :return: True if file was uploaded, else False
    """

    s3_client = boto3.client('s3',
                            region_name='us-east-1',
                            aws_access_key_id=S3_KEY,
                            aws_secret_access_key=S3_SECRET)

    try:

        s3_client.put_object(
            Body=file,
            Bucket=S3_BUCKET,
            Key=key,
            Tagging='public=yes'
        )

    except ClientError as e:
        print(e)
        return False

    return True

def generate_s3_presigned_post_for_upload(key, file_type, file_name):

    cond = True

    while cond:

        try:

            s3_client = boto3.client('s3',
                region_name='us-east-1',
                aws_access_key_id=S3_KEY,
                aws_secret_access_key=S3_SECRET
            )

            cond = False

        except:
            cond = True

    if 'image' in file_type:

        print("image detected")

        presigned_post = s3_client.generate_presigned_post(
            Bucket = S3_BUCKET,
            Key = key,
            Fields = {"Content-Type": file_type,
                    "tagging": "<Tagging><TagSet><Tag><Key>public</Key><Value>yes</Value></Tag></TagSet></Tagging>"},
            Conditions = [
            {"Content-Type": file_type},
            {"tagging": "<Tagging><TagSet><Tag><Key>public</Key><Value>yes</Value></Tag></TagSet></Tagging>"}
            ],
            ExpiresIn = 3600
        )

    else:

        presigned_post = s3_client.generate_presigned_post(
            Bucket = S3_BUCKET,
            Key = key,
            Fields = {"Content-Type": file_type,
                    "Content-Disposition": 'attachments; filename="%s"' %file_name},
            Conditions = [
            {"Content-Type": file_type},
            {"Content-Disposition": 'attachments; filename="%s"' %file_name}
            ],
            ExpiresIn = 3600
        )

    print(presigned_post)

    return json.dumps({
        'data': presigned_post,
        'url': S3_LOCATION + key
    })

def delete_files(file_dict_list):
    """
    Delete a folder from AWS S3

    :file_dict_list: dictionary of keys of objects to be deleted
    :return: True if files were deleted, else false
    """

    s3_client = boto3.client('s3',
                            region_name='us-east-1',
                            aws_access_key_id=S3_KEY,
                            aws_secret_access_key=S3_SECRET)

    try:

        bucket = s3_client.delete_objects(
            Bucket=S3_BUCKET,
            Delete={
                'Objects': file_dict_list,
                'Quiet': False
            }
        )

    except ClientError as e:
        print(e)
        return False

    return True

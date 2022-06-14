import boto3
import logging

from django.conf    import settings
from botocore.exceptions import ClientError

bucket = settings.AWS_STORAGE_BUCKET_NAME
client = boto3.client('s3')

def upload_fileobj(Fileobj, Key, ExtraArgs, Callback=None, Config=None):
    try:
        client.upload_fileobj(Fileobj, bucket, Key, ExtraArgs)

    except ClientError as e:
        logging.error(e)
        return False

<<<<<<< HEAD
    return True     

def object_delete(Key):
    try:    
        client.delete_object(
        Bucket = bucket,
        Key = Key,
    )
    except ClientError as e:
        logging.error(e)
        return False
    return True
=======
    return True

def delete_object(Bucket, Key):
    try:
        client.delete_object(Bucket=bucket, Key=Key)

    except ClientError as e:
        logging.error(e)
        return False
>>>>>>> 1d2653a ([FEAT] 댓글수정 기능)

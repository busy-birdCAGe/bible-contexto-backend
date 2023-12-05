import boto3
import random
from os import environ

BUCKET = environ["BACKEND_BUCKET"]
KEYOFTHEDAYKEY = "key_of_the_day"

s3 = boto3.client('s3')

def handler(event, context):
    keys = get_keys()
    previous_key_of_the_day = get_current_key_of_the_day()
    key_of_the_day = previous_key_of_the_day
    while key_of_the_day == previous_key_of_the_day:
        key_of_the_day = random.choice(keys)
    set_key_of_the_day(key_of_the_day)

def get_keys():
    keys = set([obj["Key"] for obj in s3.list_objects_v2(Bucket=BUCKET)["Contents"]])
    return list(keys - set(KEYOFTHEDAYKEY))
    
def set_key_of_the_day(word):
    s3.put_object(Bucket=BUCKET, Key=KEYOFTHEDAYKEY, Body=word)

def get_current_key_of_the_day():
    return s3.get_object(Bucket=BUCKET, Key=KEYOFTHEDAYKEY)["Body"].read().decode()
import boto3
from botocore.exceptions import ClientError
import random
from os import environ
import json

LANGUAGE = environ["language"]
BUCKET = environ["BACKEND_BUCKET"]
KEYOFTHEDAYKEY = "key_of_the_day"
WORDTOIDMAPPING = "word_to_id_mapping"
DAILYGAMESKEY = "daily_games"

s3 = boto3.client('s3')

def handler(event, context):

    with open(f"{LANGUAGE}.csv", "r") as f:
        words = f.read().split("\n")

    word_to_id_mapping = get_word_to_id_mapping()

    previous_key_of_the_day = get_current_key_of_the_day()

    key_of_the_day = previous_key_of_the_day
    while key_of_the_day == previous_key_of_the_day:
        word_of_the_day = random.choice(words)
        key_of_the_day = word_to_id_mapping[word_of_the_day]

    update_daily_games_list(key_of_the_day)
    print(f"[{LANGUAGE}] Word of the day: {word_of_the_day}")

def get_current_key_of_the_day():
    try:
        return s3.get_object(Bucket=BUCKET, Key=LANGUAGE + "/" + KEYOFTHEDAYKEY)["Body"].read().decode()
    except:
        return ""
    
def get_word_to_id_mapping():
    return json.loads(s3.get_object(Bucket=BUCKET, Key=LANGUAGE + "/" + WORDTOIDMAPPING)["Body"].read().decode())

def update_daily_games_list(key_of_the_day):
    try:
        current_list = s3.get_object(Bucket=BUCKET, Key=LANGUAGE + "/" + DAILYGAMESKEY)["Body"].read().decode()
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            current_list = ""
        else:
            raise e
    lines = [line for line in current_list.split("\n") if line]
    last_key = lines[-1].split(",")[0] if current_list else "0"
    lines.append(f"{int(last_key)+1},{key_of_the_day}")
    s3.put_object(Bucket=BUCKET, Key=LANGUAGE + "/" + DAILYGAMESKEY, Body="\n".join(lines))
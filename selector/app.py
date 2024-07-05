import boto3
import random
from os import environ
import json

LANGUAGE = environ["language"]
BUCKET = environ["BACKEND_BUCKET"]
KEYOFTHEDAYKEY = "key_of_the_day"
WORDTOIDMAPPING = "word_to_id_mapping"

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

    set_key_of_the_day(key_of_the_day)
    print(f"[{LANGUAGE}] Word of the day: {word_of_the_day}")
    
def set_key_of_the_day(word):
    s3.put_object(Bucket=BUCKET, Key=LANGUAGE + "/" + KEYOFTHEDAYKEY, Body=word)

def get_current_key_of_the_day():
    try:
        return s3.get_object(Bucket=BUCKET, Key=LANGUAGE + "/" + KEYOFTHEDAYKEY)["Body"].read().decode()
    except:
        return ""
    
def get_word_to_id_mapping():
    return json.loads(s3.get_object(Bucket=BUCKET, Key=LANGUAGE + "/" + WORDTOIDMAPPING)["Body"].read().decode())
import json
import zipfile
import boto3
import random
from os import environ

BUCKET = environ["BACKEND_BUCKET"]
word_of_the_day_key = "word_of_the_day"
vectors_zip = "vectors.zip"
vectors_file = "vectors.json"

s3 = boto3.client('s3')

def handler(event, context):
    vectors = load_vectors()
    words = load_word_list()
    word_of_the_day = event.get("word") or choose_word(words)
    if not word_exists(word_of_the_day):
        word_list = get_sorted_list(word_of_the_day, vectors)
        upload_words_to_s3(word_of_the_day, word_list)
    set_word_of_the_day(word_of_the_day)

def load_vectors():
    with zipfile.ZipFile(vectors_zip, 'r') as zip_ref:
        with zip_ref.open(vectors_file) as f:
            return json.loads(f.read())
        
def load_word_list():
    with open("words.csv", "r") as f:
        return f.read().split("\n")
    
def choose_word(words):
    return random.choice(words)

def dot(A,B): 
    return (sum(a*b for a,b in zip(A,B)))

def cosine_similarity(a,b):
    return dot(a,b) / ( (dot(a,a) **.5) * (dot(b,b) ** .5) )

def get_sorted_list(base_word, vectors):
    similarity_scores = []
    for word in vectors:
        if sum(vectors[word]) != 0:
            similarity_scores.append([word, cosine_similarity(vectors[base_word], vectors[word])])
    sorted_list = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    return [item[0] for item in sorted_list]

def upload_words_to_s3(base_word, word_list):
    s3.put_object(Bucket=BUCKET, Key=base_word, Body=",".join(word_list))

def word_exists(key):
    try:
        s3.head_object(Bucket=BUCKET, Key=key)
        return True
    except Exception:
        return False
    
def set_word_of_the_day(word):
    s3.put_object(Bucket=BUCKET, Key=word_of_the_day_key, Body=word)

import json
import zipfile
from scipy.spatial.distance import cosine
import boto3
import random
from os import environ

BUCKET = environ["BACKEND_BUCKET"]
FRONTEND_BUCKET = environ["FRONTEND_BUCKET"]
word_of_the_day_key = "word_of_the_day.ts"
vectors_zip = "vectors.zip"
vectors_file = "vectors.json"

s3 = boto3.client('s3')

def handler(event, context):
    vectors = load_vectors()
    word_of_the_day = choose_word(vectors)
    set_word_of_the_day(word_of_the_day)
    if not word_exists(word_of_the_day):
        word_list = get_sorted_list(word_of_the_day, vectors)
        upload_words_to_s3(word_of_the_day, word_list)

def load_vectors():
    with zipfile.ZipFile(vectors_zip, 'r') as zip_ref:
        with zip_ref.open(vectors_file) as f:
            return json.loads(f.read())
    
def choose_word(vectors):
    return random.choice(list(vectors.keys()))
    
def compare_vectors(vector_a, vector_b):
    return 1 - cosine(vector_a, vector_b)

def get_sorted_list(base_word, vectors):
    similarity_scores = []
    for word in vectors:
        if sum(vectors[word]) != 0:
            similarity_scores.append([word, compare_vectors(vectors[base_word], vectors[word])])
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
    s3.put_object(Bucket=BUCKET, Key=word_of_the_day_key, Body="export const word_of_the_day = " + word + ";")

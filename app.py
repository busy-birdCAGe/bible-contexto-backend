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
    word_of_the_day = choose_word(vectors)
    if not word_exists(word_of_the_day):
        word_list = get_sorted_list(word_of_the_day, vectors)
        upload_words_to_s3(word_of_the_day, word_list)
    set_word_of_the_day(word_of_the_day)

def load_vectors():
    with zipfile.ZipFile(vectors_zip, 'r') as zip_ref:
        with zip_ref.open(vectors_file) as f:
            return json.loads(f.read())
    
def choose_word(vectors):
    return random.choice(list(vectors.keys()))
    
def dot_product(vector_a, vector_b):
    return sum(x * y for x, y in zip(vector_a, vector_b))

def magnitude(vector):
    return sum(x ** 2 for x in vector) ** 0.5

def compare_vectors(vector_a, vector_b):
    dot = dot_product(vector_a, vector_b)
    norm_a = magnitude(vector_a)
    norm_b = magnitude(vector_b)

    if norm_a == 0 or norm_b == 0:
        return 0

    cosine_similarity = dot / (norm_a * norm_b)
    return cosine_similarity

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
    s3.put_object(Bucket=BUCKET, Key=word_of_the_day_key, Body=word)

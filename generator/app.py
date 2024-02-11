import json
import zipfile
import boto3
from os import environ

BUCKET = environ["BACKEND_BUCKET"]
vectors_zip = "vectors.zip"
vectors_file = "vectors.json"

s3 = boto3.client('s3')

def handler(event, context):
    word = event["word"]
    word_id = event["id"]
    vectors = load_vectors()
    word_list = get_sorted_list(word, vectors)
    upload_words_to_s3(word_id, word_list)

def load_vectors():
    with zipfile.ZipFile(vectors_zip, 'r') as zip_ref:
        with zip_ref.open(vectors_file) as f:
            return json.loads(f.read())

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
import boto3
import json
import zipfile
from uuid import uuid4

language = "spanish"
backend_bucket = "dev-bible-contexto-backend"
vectors_zip = f"generator/vectors/{language}.zip"
vectors_file = "vectors.json"

def bulk_delete_s3_objects(bucket_name, keys):
    s3 = boto3.client('s3')
    deleted_objects = []
    for i in range(0, len(keys), 1000):
        delete_batch = [{'Key': key} for key in keys[i:i+1000]]
        response = s3.delete_objects(
            Bucket=bucket_name,
            Delete={'Objects': delete_batch}
        )
        deleted_objects.extend(obj['Key'] for obj in response.get('Deleted', []))
    return deleted_objects

s3 = boto3.resource('s3')
bucket = s3.Bucket(backend_bucket)

keys = []
for obj in bucket.objects.all():
    keys.append(obj.key)

bulk_delete_s3_objects(backend_bucket, keys)

with zipfile.ZipFile(vectors_zip, 'r') as zip_ref:
    with zip_ref.open(vectors_file) as f:
        vectors = json.loads(f.read())

lambda_client = boto3.client('lambda', region_name="us-east-1")

word_to_id_mapping = {}
for word in vectors:
    word_id = str(uuid4())
    lambda_client.invoke(
        FunctionName="dev-bible-contexto-backend-Generator-Ak2F3Y2B6x0Z",
        InvocationType='Event',
        Payload=json.dumps({"word": word, "id": word_id, "language": language})
    )
    word_to_id_mapping[word] = word_id
    print(word)

s3_client = boto3.client('s3')

s3_client.put_object(Bucket=backend_bucket, Key=language+"/word_to_id_mapping", Body=json.dumps(word_to_id_mapping))

with open("data/"+language+"/guess_words.txt", "r") as f:
    s3_client.put_object(Bucket=backend_bucket, Key=language+"/"+"guess_words.txt", Body=f.read())

with open("data/"+language+"/stop_words.txt", "r") as f:
    s3_client.put_object(Bucket=backend_bucket, Key=language+"/"+"stop_words.txt", Body=f.read())
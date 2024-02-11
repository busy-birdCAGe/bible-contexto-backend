import boto3
import json
from time import sleep
import zipfile
from uuid import uuid4

backend_bucket = "dev-bible-contexto-backend"
vectors_zip = "generator\\vectors.zip"
vectors_file = "vectors.json"

s3 = boto3.client('s3')
objects = s3.list_objects_v2(Bucket=backend_bucket)
if 'Contents' in objects:
    for obj in objects['Contents']:
        s3.delete_object(Bucket=backend_bucket, Key=obj['Key'])
        print(f"Deleted object: {obj['Key']}")
else:
    print("No objects found in the bucket.")

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
        Payload=json.dumps({"word": word, "id": word_id})
    )
    word_to_id_mapping[word] = word_id
    print(word)
    sleep(0.1)

s3.put_object(Bucket=backend_bucket, Key="word_to_id_mapping", Body=json.dumps(word_to_id_mapping))
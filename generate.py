import boto3
import json
from time import sleep

with open("words.csv", "r") as f:
    words = f.read().split("\n")

lambda_client = boto3.client('lambda', region_name="us-east-1")

for word in words:

    lambda_client.invoke(
        FunctionName="prod-bible-contexto-backend-Generator-xyYv4xsH5pZm",
        InvocationType='Event',
        Payload=json.dumps({"word": word})
    )
    sleep(0.5)

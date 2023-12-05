import boto3
import json

with open("words.csv", "r") as f:
    words = f.read().split("\n")

lambda_client = boto3.client('lambda', region_name="us-east-1")

for word in ["lord"]:

    lambda_client.invoke(
        FunctionName="dev-bible-contexto-backend-App-UuZTgkwpwILP",
        InvocationType='Event',
        Payload=json.dumps({"word": word})
    )

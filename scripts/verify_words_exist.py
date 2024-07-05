import json
import zipfile

with zipfile.ZipFile("generator/vectors/spanish.zip", 'r') as zip_ref:
    with zip_ref.open("vectors.json") as f:
        vectors = json.loads(f.read())

word_list = list(vectors.keys())

with open("selector/words.csv", "r") as f:
    word_choices = f.read().split("\n")

for word_choice in word_choices:
    if word_choice not in word_list:
        print(f"{word_choice} not in vectors")
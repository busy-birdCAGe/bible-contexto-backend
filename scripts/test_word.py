import json
import zipfile

language = "spanish"

def load_vectors(language):
    with zipfile.ZipFile(f"generator/vectors/spanish.zip", 'r') as zip_ref:
        with zip_ref.open("vectors.json") as f:
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


vectors = load_vectors(language)

sorted_words = get_sorted_list("fueg", vectors)

print("\n".join(sorted_words[:100]))
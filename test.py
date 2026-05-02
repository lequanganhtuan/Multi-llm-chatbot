from google import genai

client = genai.Client(api_key='AIzaSyDv8TUfDn7U6s-kfyG2gW9aUfTQc7-xt8A')

models = client.models.list()

for m in models:
    print(m.name)
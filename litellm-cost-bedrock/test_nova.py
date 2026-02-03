import sys
from openai import OpenAI

client = OpenAI(
    api_key="anything",
    base_url="http://localhost:4000"
)

response = client.chat.completions.create(
    model="nova-2-lite",
    messages=[{"role": "user", "content": sys.argv[1]}]
)

print(response.choices[0].message.content)

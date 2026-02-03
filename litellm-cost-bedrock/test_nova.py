import sys
from openai import OpenAI

client = OpenAI(
    api_key="anything",
    base_url="http://localhost:4000"
)

# NOTE: Using with_raw_response to access HTTP headers
# Without this, the OpenAI SDK doesn't expose the x-litellm-response-cost header
# that contains the actual cost information from LiteLLM
response = client.chat.completions.with_raw_response.create(
    model="nova-2-lite",
    messages=[{"role": "user", "content": sys.argv[1]}]
)

# Extract the parsed response
completion = response.parse()
print(completion.choices[0].message.content)

# Get cost from response headers
cost = response.headers.get("x-litellm-response-cost")
if cost:
    print(f"\nCost: ${float(cost):.6f}")
else:
    print(f"\nTokens: {completion.usage.total_tokens}")

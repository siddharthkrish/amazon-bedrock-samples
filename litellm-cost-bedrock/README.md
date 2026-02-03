# LiteLLM Proxy for Amazon Bedrock

A simple LiteLLM proxy configuration to access Amazon Bedrock models through an OpenAI-compatible API.

## Setup

1. **Install dependencies**:
```bash
uv sync
```

2. **Configure AWS credentials**:
```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

Or use AWS CLI credentials (recommended):
```bash
aws configure
```

3. **Start the proxy**:
```bash
uv run litellm --config config.yaml
```

The proxy will run at `http://0.0.0.0:4000`

## Usage

### Using curl:
```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Using OpenAI Python SDK:
```python
import openai

client = openai.OpenAI(
    api_key="anything",
    base_url="http://localhost:4000"
)

response = client.chat.completions.create(
    model="claude-3-5-sonnet",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

## Available Models

- `claude-3-5-sonnet` - Anthropic Claude 3.5 Sonnet
- `claude-3-haiku` - Anthropic Claude 3 Haiku

## Adding More Models

Edit `config.yaml` and add models from the [Bedrock documentation](https://docs.litellm.ai/docs/providers/bedrock).

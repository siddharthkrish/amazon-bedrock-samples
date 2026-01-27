# Bedrock Claude CLI

A command-line tool to interact with Claude Opus 4.5 on Amazon Bedrock. Supports multiple file inputs (images, PDFs, documents) and automatically saves generated files.

## Features

- 📁 Multiple file input support (images, PDFs, documents)
- 📝 Prompt from file
- 💾 Automatic file output detection and saving
- 🎨 Support for images (PNG, JPG, GIF, WebP)
- 📄 Support for documents (PDF, CSV, DOCX, XLSX, HTML, TXT, MD)
- ⚙️ Configurable AWS region and profile
- 🔧 Adjustable temperature and max tokens

## Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- AWS credentials configured with access to Amazon Bedrock
- Access to Claude Opus 4.5 model in your AWS account

## Installation

1. Install `uv` if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone or download this project:
```bash
cd bedrock_file_example
```

3. Install dependencies and the CLI tool:
```bash
uv pip install -e .
```

Or use uv's sync command:
```bash
uv sync
```

## AWS Configuration

Make sure you have AWS credentials configured. You can use:

- AWS CLI configuration (`~/.aws/credentials`)
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- IAM role (if running on EC2/ECS)

The IAM user/role needs permissions to invoke Bedrock models:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/us.anthropic.claude-opus-4-5-v1:0"
    }
  ]
}
```

## Usage

### Basic Usage

```bash
bedrock-claude -p prompt.txt
```

### With Files

```bash
bedrock-claude -p prompt.txt -f image.png -f document.pdf
```

### With Custom Output Directory

```bash
bedrock-claude -p prompt.txt -f data.csv -o ./my-outputs
```

### With AWS Profile and Region

```bash
bedrock-claude -p prompt.txt --profile my-profile --region us-west-2
```

### Full Example

```bash
bedrock-claude \
  --prompt-file prompt.txt \
  --file screenshot.png \
  --file report.pdf \
  --file data.csv \
  --output-dir ./outputs \
  --region us-east-1 \
  --max-tokens 8192 \
  --temperature 0.7
```

## Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--prompt-file` | `-p` | File containing the prompt (required) | - |
| `--file` | `-f` | Input file (can be used multiple times) | - |
| `--output-dir` | `-o` | Directory for output files | `./output` |
| `--region` | `-r` | AWS region | `us-east-1` |
| `--profile` | - | AWS profile name | default |
| `--max-tokens` | - | Maximum tokens in response | `4096` |
| `--temperature` | - | Temperature (0.0-1.0) | `1.0` |
| `--save-output` | - | Save output to file | `True` |
| `--no-save-output` | - | Don't save output | `False` |

## Example Prompts

### Generate Code
Create `prompt.txt`:
```
Create a Python script that processes CSV files and generates a summary report.
```

Run:
```bash
bedrock-claude -p prompt.txt -o ./code-output
```

### Analyze an Image
Create `analyze-image.txt`:
```
Analyze this image and describe what you see in detail.
```

Run:
```bash
bedrock-claude -p analyze-image.txt -f photo.jpg
```

### Process Multiple Documents
Create `summarize.txt`:
```
Please read all the provided documents and create a comprehensive summary.
```

Run:
```bash
bedrock-claude -p summarize.txt -f doc1.pdf -f doc2.pdf -f notes.txt
```

## Output Handling

The CLI automatically detects if Claude's response should be saved as a file based on:

- Presence of code blocks (```...```)
- Long text output (>5000 characters)
- Structured data (JSON, XML)

Files are saved to the output directory with appropriate extensions:
- Code blocks: `output_1.txt`, `output_2.txt`, etc.
- JSON: `output.json`
- XML: `output.xml`
- Other: `output.txt`

Regular conversational responses are displayed in the console.

## Supported File Types

### Images
- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- GIF (`.gif`)
- WebP (`.webp`)

### Documents
- PDF (`.pdf`)
- CSV (`.csv`)
- Word (`.doc`, `.docx`)
- Excel (`.xls`, `.xlsx`)
- HTML (`.html`)
- Text (`.txt`)
- Markdown (`.md`)

## Troubleshooting

### "Access Denied" Error
Make sure your AWS credentials have permission to invoke Bedrock models and that you have access to Claude Opus 4.5 in your region.

### Model Not Available
Claude Opus 4.5 might not be available in all regions. Try `us-east-1` or `us-west-2`.

### File Not Found
Ensure all file paths are correct and files exist before running the command.

## Development

To run the CLI during development without installation:

```bash
uv run python -m bedrock_claude_cli.main -p prompt.txt
```

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

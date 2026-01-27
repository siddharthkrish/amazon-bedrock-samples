#!/usr/bin/env python3
"""
CLI tool to interact with Claude Opus 4.5 on Amazon Bedrock.
Supports multiple file inputs and saves generated files.
"""

import json
import base64
import mimetypes
import sys
from pathlib import Path
from typing import List, Optional

import boto3
import click


# Model ID for Claude Opus 4.5 on Bedrock
MODEL_ID = "global.anthropic.claude-opus-4-5-20251101-v1:0"

# Supported image formats
IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

# Supported document formats (only PDF for Bedrock document type)
DOCUMENT_FORMATS = {'.pdf'}

# Text extraction formats (will be converted to text)
TEXT_EXTRACTION_FORMATS = {'.csv', '.doc', '.docx', '.xls', '.xlsx', '.html', '.txt', '.md'}


def encode_file(file_path: Path) -> tuple[str, str]:
    """
    Encode a file to base64 and determine its media type.
    
    Returns:
        tuple: (base64_data, media_type)
    """
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    base64_data = base64.standard_b64encode(file_data).decode('utf-8')
    
    # Determine media type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type is None:
        # Default to appropriate type based on extension
        ext = file_path.suffix.lower()
        if ext in IMAGE_FORMATS:
            mime_type = f"image/{ext[1:]}" if ext != '.jpg' else "image/jpeg"
        elif ext == '.pdf':
            mime_type = "application/pdf"
        else:
            mime_type = "text/plain"
    
    return base64_data, mime_type


def extract_text_from_docx(file_path: Path) -> str:
    """Extract text content from a DOCX file."""
    try:
        from docx import Document
        doc = Document(file_path)
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        return '\n'.join(text_parts)
    except ImportError:
        raise ImportError("python-docx is required to process .docx files. Install with: pip install python-docx")


def process_files(file_paths: List[str]) -> List[dict]:
    """
    Process input files and create content blocks for the API.
    
    Args:
        file_paths: List of file paths to process
        
    Returns:
        List of content blocks for the API request
    """
    content_blocks = []
    
    for file_path_str in file_paths:
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            click.echo(f"Warning: File not found: {file_path}", err=True)
            continue
        
        ext = file_path.suffix.lower()
        
        if ext in IMAGE_FORMATS:
            # Process as image
            base64_data, media_type = encode_file(file_path)
            content_blocks.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64_data
                }
            })
            click.echo(f"Added image: {file_path.name}", err=True)
            
        elif ext in DOCUMENT_FORMATS:
            # Process as PDF document (only PDF supported by Bedrock)
            base64_data, media_type = encode_file(file_path)
            content_blocks.append({
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": base64_data
                }
            })
            click.echo(f"Added PDF document: {file_path.name}", err=True)
            
        elif ext in TEXT_EXTRACTION_FORMATS:
            # Extract text from document formats
            try:
                if ext in {'.docx'}:
                    text_content = extract_text_from_docx(file_path)
                    content_blocks.append({
                        "type": "text",
                        "text": f"[Content from {file_path.name}]\n\n{text_content}"
                    })
                    click.echo(f"Added text from DOCX: {file_path.name}", err=True)
                else:
                    # Try to read as plain text
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                    content_blocks.append({
                        "type": "text",
                        "text": f"[Content from {file_path.name}]\n\n{text_content}"
                    })
                    click.echo(f"Added text file: {file_path.name}", err=True)
            except Exception as e:
                click.echo(f"Warning: Could not process file {file_path}: {e}", err=True)
        else:
            # Try to read as text
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                content_blocks.append({
                    "type": "text",
                    "text": f"[Content from {file_path.name}]\n\n{text_content}"
                })
                click.echo(f"Added text file: {file_path.name}", err=True)
            except Exception as e:
                click.echo(f"Warning: Could not process file {file_path}: {e}", err=True)
    
    return content_blocks


def call_bedrock_claude(
    prompt: str,
    files: List[str],
    region: str,
    max_tokens: int,
    temperature: float,
    profile: Optional[str] = None
) -> dict:
    """
    Call Claude Opus 4.5 on Amazon Bedrock.
    
    Args:
        prompt: The text prompt
        files: List of file paths to include
        region: AWS region
        max_tokens: Maximum tokens in response
        temperature: Temperature for generation
        profile: AWS profile name (optional)
        
    Returns:
        API response dictionary
    """
    # Initialize boto3 client
    session_kwargs = {}
    if profile:
        session_kwargs['profile_name'] = profile
    
    session = boto3.Session(**session_kwargs)
    bedrock_runtime = session.client('bedrock-runtime', region_name=region)
    
    # Build content blocks
    content_blocks = []
    
    # Add files first
    if files:
        file_blocks = process_files(files)
        content_blocks.extend(file_blocks)
    
    # Add text prompt
    content_blocks.append({
        "type": "text",
        "text": prompt
    })
    
    # Prepare the request body
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": content_blocks
            }
        ]
    }
    
    # Make the API call
    click.echo("Calling Claude Opus 4.5 on Bedrock...", err=True)
    
    response = bedrock_runtime.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(request_body)
    )
    
    # Parse response
    response_body = json.loads(response['body'].read())
    
    return response_body


def extract_and_save_output(response: dict, output_dir: Path) -> str:
    """
    Extract content from response and save files if needed.
    
    Args:
        response: API response
        output_dir: Directory to save output files
        
    Returns:
        Text content to display
    """
    content_blocks = response.get('content', [])
    text_output = []
    file_count = 0
    
    for block in content_blocks:
        if block.get('type') == 'text':
            text_output.append(block.get('text', ''))
        # Handle any other content types if needed
    
    combined_text = '\n'.join(text_output)
    
    # Check if output looks like it should be saved as a file
    # Look for common file indicators in the text
    should_save = any([
        '```' in combined_text,  # Code blocks
        len(combined_text) > 5000,  # Long output
        combined_text.strip().startswith('<?xml'),  # XML
        combined_text.strip().startswith('{') or combined_text.strip().startswith('['),  # JSON
    ])
    
    if should_save and output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to determine file type from content
        text_stripped = combined_text.strip()
        
        if '```' in combined_text:
            # Extract code blocks
            import re
            code_blocks = re.findall(r'```[\w]*\n(.*?)```', combined_text, re.DOTALL)
            for i, code in enumerate(code_blocks):
                file_count += 1
                output_file = output_dir / f"output_{file_count}.txt"
                output_file.write_text(code.strip())
                click.echo(f"Saved code block to: {output_file}", err=True)
        elif text_stripped.startswith('{') or text_stripped.startswith('['):
            output_file = output_dir / "output.json"
            output_file.write_text(combined_text)
            click.echo(f"Saved JSON output to: {output_file}", err=True)
            file_count += 1
        elif text_stripped.startswith('<?xml'):
            output_file = output_dir / "output.xml"
            output_file.write_text(combined_text)
            click.echo(f"Saved XML output to: {output_file}", err=True)
            file_count += 1
        else:
            output_file = output_dir / "output.txt"
            output_file.write_text(combined_text)
            click.echo(f"Saved output to: {output_file}", err=True)
            file_count += 1
    
    return combined_text


@click.command()
@click.option(
    '--prompt-file', '-p',
    type=click.Path(exists=True),
    required=True,
    help='File containing the prompt text'
)
@click.option(
    '--file', '-f',
    'files',
    multiple=True,
    type=click.Path(exists=True),
    help='Input files to include (images, PDFs, documents). Can be specified multiple times.'
)
@click.option(
    '--output-dir', '-o',
    type=click.Path(),
    default='./output',
    help='Directory to save generated files (default: ./output)'
)
@click.option(
    '--region', '-r',
    default='us-east-1',
    help='AWS region (default: us-east-1)'
)
@click.option(
    '--profile',
    default=None,
    help='AWS profile name (optional)'
)
@click.option(
    '--max-tokens',
    default=4096,
    help='Maximum tokens in response (default: 4096)'
)
@click.option(
    '--temperature',
    default=1.0,
    type=float,
    help='Temperature for generation (default: 1.0)'
)
@click.option(
    '--save-output/--no-save-output',
    default=True,
    help='Save output to file if it looks like generated content (default: True)'
)
def cli(prompt_file, files, output_dir, region, profile, max_tokens, temperature, save_output):
    """
    Call Claude Opus 4.5 on Amazon Bedrock with files and prompt.
    
    Example usage:
    
        bedrock-claude -p prompt.txt -f image1.png -f document.pdf -o ./outputs
    """
    try:
        # Read prompt from file
        prompt_path = Path(prompt_file)
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
        
        if not prompt.strip():
            click.echo("Error: Prompt file is empty", err=True)
            sys.exit(1)
        
        click.echo(f"Loaded prompt from: {prompt_path}", err=True)
        
        # Call the API
        response = call_bedrock_claude(
            prompt=prompt,
            files=list(files),
            region=region,
            max_tokens=max_tokens,
            temperature=temperature,
            profile=profile
        )
        
        # Extract and display/save output
        output_path = Path(output_dir) if save_output else None
        text_output = extract_and_save_output(response, output_path)
        
        # Display the output
        click.echo("\n" + "="*80)
        click.echo("CLAUDE'S RESPONSE:")
        click.echo("="*80 + "\n")
        click.echo(text_output)
        
        # Display usage information
        usage = response.get('usage', {})
        if usage:
            click.echo("\n" + "="*80, err=True)
            click.echo(f"Input tokens: {usage.get('input_tokens', 0)}", err=True)
            click.echo(f"Output tokens: {usage.get('output_tokens', 0)}", err=True)
            click.echo("="*80, err=True)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()

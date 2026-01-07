# Bedrock Code Generation

A Python-based AWS Lambda function that leverages AWS Bedrock's Converse API to generate code in various programming languages using AI models.

## ⚠️ Important Notice

**This is a demonstration project and is NOT production-ready.** It is intended for learning, testing, and experimentation purposes only. Do not use this code in production environments without proper security hardening, error handling improvements, monitoring, and compliance review.

## Overview

This Lambda function uses a two-step code generation process powered by AWS Bedrock's Qwen3-Coder model:

1. **Task Decomposition**: The user's request is analyzed and broken down into numbered steps
2. **Code Generation**: Code is generated based on the decomposed steps in the specified programming language

## Features

- **AI-Powered Code Generation**: Utilizes AWS Bedrock's `qwen.qwen3-coder-480b-a35b-v1:0` model
- **Multi-Language Support**: Generate code in any programming language by specifying the `code_language` parameter
- **Two-Step Process**: Ensures better code quality through task analysis before generation
- **Error Handling**: Includes basic validation and error responses
- **Type Hints**: Fully type-annotated Python code for better maintainability

## Architecture

```
User Request → Lambda Handler → Task Decomposition (Bedrock) → Code Generation (Bedrock) → Response
```

## Configuration

The function is configured with the following defaults:

- **Region**: `eu-north-1`
- **Model**: `qwen.qwen3-coder-480b-a35b-v1:0`
- **Max Tokens**: 2048
- **Temperature**: 0.2
- **Timeout**: 300 seconds
- **Max Retries**: 3

## Input Format

The Lambda function expects an event with the following parameters:

```json
{
  "message": "Description of the code you want to generate",
  "code_language": "python"
}
```

### Parameters

- `message` (required): A clear description of what code you want to generate
- `code_language` (required): The target programming language (e.g., "python", "javascript", "java", "go")

## Output Format

### Success Response (200)

```json
{
  "statusCode": 200,
  "body": "{\"code\": \"generated code here\"}"
}
```

### Error Responses

**Missing Parameters (400)**

```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Missing required parameter: message\"}"
}
```

**Server Error (500)**

```json
{
  "statusCode": 500,
  "body": "{\"error\": \"error details\"}"
}
```

## Dependencies

Install the required dependencies from [requirements.txt](requirements.txt):

```bash
pip install -r requirements.txt
```

Required packages:
- `boto3` - AWS SDK for Python
- `python-dotenv` - Environment variable management
- `pydantic` - Data validation
- `boto3-stubs[bedrock-runtime,bedrock,lambda,s3]` - Type stubs for boto3

## Prerequisites

1. **AWS Account**: An active AWS account with access to Bedrock
2. **Bedrock Model Access**: Enable access to the Qwen3-Coder model in your AWS region
3. **IAM Permissions**: The Lambda execution role must have permissions to invoke Bedrock:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel",
           "bedrock:InvokeModelWithResponseStream"
         ],
         "Resource": "arn:aws:bedrock:*::foundation-model/*"
       }
     ]
   }
   ```

## Example Usage

### Example 1: Generate Python Function

**Input:**
```json
{
  "message": "Create a function that calculates the Fibonacci sequence up to n terms",
  "code_language": "python"
}
```

### Example 2: Generate JavaScript Code

**Input:**
```json
{
  "message": "Create a React component for a user profile card with name, email, and avatar",
  "code_language": "javascript"
}
```

## Code Structure

- `lambda_handler()`: Main entry point for the Lambda function
- `generate_code_using_bedrock()`: Orchestrates the two-step code generation process
- `_call_bedrock()`: Wrapper for AWS Bedrock Converse API calls
- `_extract_text()`: Utility to parse text from Bedrock response messages

## Limitations

- Maximum token output: 2048 tokens
- Timeout: 300 seconds
- The generated code should be reviewed and tested before use
- Model availability depends on AWS region and account access

## Future Improvements

Potential enhancements for production use:

- Add authentication and authorization
- Implement request throttling and rate limiting
- Add comprehensive logging and monitoring
- Store generation history and results
- Add code validation and security scanning
- Support streaming responses for longer code generation
- Add caching for similar requests
- Implement cost tracking and optimization

## License

This project is provided as-is for educational and demonstration purposes.

## Contributing

This is a demonstration project. Feel free to fork and modify for your own learning purposes.

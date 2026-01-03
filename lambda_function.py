import boto3
import json
from botocore.config import Config
from botocore.exceptions import ClientError
from typing import Any

REGION: str = "eu-north-1"
CODER_MODEL_ID: str = "qwen.qwen3-coder-480b-a35b-v1:0"
PROMPT_CODE_SECTION_DELIMITER: str = "\n###\n"

bedrock_runtime: Any = boto3.client(
    "bedrock-runtime",
    region_name=REGION,
    config=Config(connect_timeout=5, read_timeout=300, retries={"max_attempts": 3}),
)

def _extract_text(message: dict[str, Any]) -> str:
    """
    Extract text content from a Bedrock message structure.
    
    Args:
        message: Bedrock message dictionary containing content blocks
    
    Returns:
        str: Extracted text from the first text block, or empty string if not found
    """
    content: list[Any] = message.get("content", [])
    text: str = next((b["text"] for b in content if isinstance(b, dict) and "text" in b), "")
    return text

def _call_bedrock(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Call AWS Bedrock Converse API with configured model and inference settings.
    
    Args:
        messages: Conversation messages in Bedrock format
    
    Returns:
        Bedrock API response containing the model's output
    """
    return bedrock_runtime.converse(
        modelId=CODER_MODEL_ID,
        system=[{"text": "You are a lead software engineer. Be clear and concise."}],
        messages=messages,
        inferenceConfig={"maxTokens": 2048, "temperature": 0.2},
    )

def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    AWS Lambda handler for generating code using AWS Bedrock.
    
    Args:
        event: Lambda event containing:
            - message (str): The code generation request description
            - code_language (str): The target programming language
        context: Lambda context object
    
    Returns:
        dict: Response with statusCode and body containing:
            - 200: {'code': generated_code_string}
            - 400: {'error': validation_error_message}
            - 500: {'error': exception_message}
    """
    try:
        # Validate required input parameters
        if "message" not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required parameter: message'})
            }
        if "code_language" not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required parameter: code_language'})
            }
        
        message: str = event["message"]
        code_language: str = event["code_language"]

        generated_code: str = generate_code_using_bedrock(message, code_language)

        return {
            'statusCode': 200,
            'body': json.dumps({'code': generated_code})
        }
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def generate_code_using_bedrock(message: str, code_language: str) -> str:
    """
    Generate code using AWS Bedrock's Converse API with a two-step process.
    
    First, the task is decomposed into steps, then code is generated based on those steps.
    
    Args:
        message: Description of the code to generate
        code_language: Target programming language for the generated code
    
    Returns:
        str: The generated code as a string
    
    Raises:
        Exception: If Bedrock API calls fail or response parsing fails
    """

    task_analysis_prompt: str = (
        f"Analyze the following request and determine the necessary steps to accomplish it in {code_language}:"
        f"{PROMPT_CODE_SECTION_DELIMITER}{message}{PROMPT_CODE_SECTION_DELIMITER}"
        "Respond only with a numbered list of steps, nothing else."
    )

    code_generation_prompt: str = (
        f"Generate the {code_language} code according to the previously defined steps."
        "Take your time to ensure accuracy and completeness."
        "Respond only with the generated code, nothing else."
    )

    body: list[Any] = [
        {"role": "user", "content": [{"text": task_analysis_prompt}]}
    ]

    try:
        task_decomposition_response: Any = _call_bedrock(body)
        task_decomposition_text: Any = task_decomposition_response["output"]["message"]
        body.append(task_decomposition_text)
        body.append({"role": "user", "content": [{"text": code_generation_prompt}]})
        
        code_generation_response: Any = _call_bedrock(body)
        code_generation_response_text: Any = code_generation_response["output"]["message"]
        generated_code: str = _extract_text(code_generation_response_text)
        return generated_code
    except ClientError as e:
        print(f"Error during Bedrock interaction: {e}")
        raise

"""
Nemotron API client for generating mockups
"""
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
load_dotenv()

# Configuration for NVIDIA Nemotron API
NVIDIA_API_KEY = os.environ.get('NVIDIA_API_KEY', '').strip()
NVIDIA_API_URL = os.environ.get('NVIDIA_API_URL', 'https://integrate.api.nvidia.com/v1/chat/completions').strip()


def call_nvidia_nemotron(prompt: str, system_message: str) -> str:
    """
    Call NVIDIA Nemotron API to generate content
    
    Args:
        prompt: User prompt/request
        system_message: System message/instructions
    
    Returns:
        Generated content from Nemotron
    """
    if not NVIDIA_API_KEY or NVIDIA_API_KEY == '':
        raise Exception("NVIDIA_API_KEY is not set. Please create a .env file in the backend directory with your API key.")
    
    # Clean the API key (remove any quotes or whitespace)
    api_key = NVIDIA_API_KEY.strip().strip('"').strip("'")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'nvidia/llama-3.3-nemotron-super-49b-v1.5',
        'messages': [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.6,
        'top_p': 0.95,
        'max_tokens': 16000,
        'frequency_penalty': 0,
        'presence_penalty': 0,
        'stream': False
    }
    
    try:
        # Debug logging (don't log the full API key)
        print(f"Making API request to: {NVIDIA_API_URL}")
        print(f"API Key present: {bool(api_key)}, length: {len(api_key)}")
        print(f"Model: {payload['model']}")
        
        response = requests.post(NVIDIA_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        if 'choices' not in result or len(result['choices']) == 0:
            raise Exception("No choices in API response")
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"Error calling NVIDIA API (RequestException): {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
            print(f"Response status: {status_code}")
            print(f"Response body: {e.response.text}")
            
            if status_code == 401:
                raise Exception("Invalid API key. Please check your NVIDIA_API_KEY in the .env file. Get your API key from https://build.nvidia.com/")
            elif status_code == 429:
                raise Exception("Rate limit exceeded. Please wait a moment and try again.")
            elif status_code == 400:
                raise Exception(f"Invalid request: {e.response.text}")
            else:
                raise Exception(f"API request failed with status {status_code}: {e.response.text}")
        raise Exception(f"Failed to call NVIDIA API: {str(e)}")
    except Exception as e:
        print(f"Error calling NVIDIA API: {str(e)}")
        raise Exception(f"Failed to process AI request: {str(e)}")


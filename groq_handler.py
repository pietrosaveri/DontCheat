import os
import base64
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# System prompt for the VLM
SYSTEM_PROMPT = """You are an intelligent assistant that analyzes screenshots containing questions or problems.

CRITICAL RULES:
1. Provide ONLY the final answers - NO explanations, NO reasoning, NO step-by-step
2. If multiple questions, number them: "1. Answer" "2. Answer" etc.
3. For multiple choice: just state the correct letter/option
4. For math: just give the final number/result
5. For true/false: just say "True" or "False"
6. Maximum 2-3 words per answer when possible
7. Be extremely brief and direct

Example format:
1. Safe Edit
2. Status Listing
3. False
4. True

DO NOT include any reasoning, steps, or explanations."""

def analyze_screenshot(image_path):
    """
    Analyze a screenshot using Groq's VLM API.
    
    Args:
        image_path: Path to the screenshot image
        
    Returns:
        str: The AI's answer, or None if failed
    """
    try:
        # Get API key from environment
        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            print("ERROR: GROQ_API_KEY not found in environment variables")
            return "Error: Groq API key not configured"
        
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        # Read and encode image
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Create the API request
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",  # Groq's vision model
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": "Please analyze this image and answer any questions or problems you see."
                        }
                    ]
                }
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        
        # Extract the answer
        answer = response.choices[0].message.content
        return answer
        
    except Exception as e:
        print(f"Error analyzing screenshot with Groq: {e}")
        return f"Error: {str(e)}"

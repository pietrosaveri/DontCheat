import os
import base64
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

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
    Analyze a screenshot using Google's Gemini VLM API.
    
    Args:
        image_path: Path to the screenshot image
        
    Returns:
        str: The AI's answer, or None if failed
    """
    try:
        # Get API key from environment
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("ERROR: GEMINI_API_KEY not found in environment variables")
            return "Error: Gemini API key not configured"
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize the model (using Gemini 1.5 Flash for speed, or use 'gemini-1.5-pro' for better quality)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Open the image
        image = Image.open(image_path)
        
        # Create the prompt
        prompt = f"{SYSTEM_PROMPT}\n\nPlease analyze this image and answer any questions or problems you see."
        
        # Generate response
        response = model.generate_content([prompt, image])
        
        # Extract the answer
        answer = response.text
        return answer
        
    except Exception as e:
        print(f"Error analyzing screenshot with Gemini: {e}")
        return f"Error: {str(e)}"

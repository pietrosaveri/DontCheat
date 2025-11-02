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
1. For MULTIPLE CHOICE questions: provide ONLY the letter/option (e.g., "A" or "Option B")
2. For TRUE/FALSE questions: provide ONLY "True" or "False"
3. For SHORT ANSWER questions: provide a brief but complete answer (1 sentence)
4. For OPEN-ENDED questions: provide a complete, well-formed answer that fully addresses the question (2-5 sentences as needed)
5. For MATH/COMPUTATIONAL problems: provide the final answer/result, not the method
6. IMPORTANT: When asked "how to find/calculate/determine X", SOLVE IT and provide X itself, NOT instructions on how to find it
7. For problems with visual data (graphs, diagrams, tables): ANALYZE the visual data and provide the actual answer based on what you see
8. If multiple questions exist, number them: "1. Answer" "2. Answer" etc.
9. NO explanations, NO reasoning, NO step-by-step process, NO methodology descriptions - just the answer itself
10. If no questions are found in the image, return exactly: "no questions found"
11. Match the depth of your answer to the question type - be concise for objective questions, thorough for subjective ones

Example format:
1. B
2. The main theme explores the relationship between technology and human connection, highlighting how digital communication can both unite and isolate individuals.
3. False
4. 42
5. 1→3→6→8 (distance: 15)

DO NOT include any reasoning, steps, methodology, or explanations - only provide the final answers themselves."""

def analyze_screenshot(image_path, reference_image_path=None):
    """
    Analyze a screenshot using Google's Gemini VLM API.
    
    Args:
        image_path: Path to the screenshot image
        reference_image_path: Optional path to reference context image
        
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
        
        # Open the main image
        image = Image.open(image_path)
        
        # Build content list
        content = [SYSTEM_PROMPT]
        
        # Add reference image and context if provided
        if reference_image_path and os.path.exists(reference_image_path):
            reference_image = Image.open(reference_image_path)
            content.append("\n\nThis is the reference context/passage:")
            content.append(reference_image)
            content.append("\n\nUsing the reference context above, please answer the question(s) in this image:")
            content.append(image)
        else:
            content.append("\n\nPlease analyze this image and answer any questions or problems you see.")
            content.append(image)
        
        # Generate response
        response = model.generate_content(content)
        
        # Extract the answer
        answer = response.text
        return answer
        
    except Exception as e:
        print(f"Error analyzing screenshot with Gemini: {e}")
        return f"Error: {str(e)}"

import os
import base64
from groq import Groq
from dotenv import load_dotenv

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
    Analyze a screenshot using Groq's VLM API.de
    
    Args:
        image_path: Path to the screenshot image
        reference_image_path: Optional path to reference context image
        
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
        
        # Read and encode main image
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Build user content
        user_content = []
        
        # Add reference image first if provided
        if reference_image_path and os.path.exists(reference_image_path):
            with open(reference_image_path, 'rb') as ref_file:
                ref_data = base64.b64encode(ref_file.read()).decode('utf-8')
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{ref_data}"
                }
            })
            user_content.append({
                "type": "text",
                "text": "This is the reference context/passage:"
            })
        
        # Add main question image
        user_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{image_data}"
            }
        })
        
        # Add instruction text
        if reference_image_path:
            user_content.append({
                "type": "text",
                "text": "Using the reference context above, please answer the question(s) in this image."
            })
        else:
            user_content.append({
                "type": "text",
                "text": "Please analyze this image and answer any questions or problems you see."
            })
        
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
                    "content": user_content
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

import os
import base64
import io
from PIL import Image
from openai import OpenAI
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
    Analyze a screenshot using a local LLM via LM Studio (OpenAI-compatible API).
    
    Args:
        image_path: Path to the screenshot image
        reference_image_path: Optional path to reference context image
        
    Returns:
        str: The AI's answer, or None if failed
    """
    try:
        # Get configuration from environment or use defaults
        base_url = os.environ.get('LM_STUDIO_BASE_URL', 'http://localhost:1234/v1')
        api_key = os.environ.get('LM_STUDIO_API_KEY', 'lm-studio') # Key usually doesn't matter for local

        
        # Initialize OpenAI client pointing to local LM Studio
        client = OpenAI(base_url=base_url, api_key=api_key)
        
        def encode_image(path):
            """Resize and encode image to base64"""
            with Image.open(path) as img:
                # Normalize to 896x896 resolution
                img.thumbnail((896, 896))
                
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG", quality=85)
                return base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Encode main image
        image_data = encode_image(image_path)
        
        # Build user content
        user_content = []
        
        # Add reference image first if provided
        if reference_image_path and os.path.exists(reference_image_path):
            ref_data = encode_image(reference_image_path)
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{ref_data}"
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
                "url": f"data:image/jpeg;base64,{image_data}"
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
        # Note: 'model' parameter often ignored by LM Studio if only one model is loaded,
        # but good to specify a generic one or the one loaded.
        response = client.chat.completions.create(
            model="local-model", 
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
        print(f"Error analyzing screenshot with LM Studio: {e}")
        return f"Error: {str(e)}"

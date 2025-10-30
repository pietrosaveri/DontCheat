import os
import base64
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# System prompt for the VLM
SYSTEM_PROMPT = """You are an expert database assistant specializing in MongoDB and Neo4j.

YOUR EXPERTISE:
- MongoDB: queries, aggregations, CRUD operations, indexing, schema design
- Neo4j: Cypher queries, graph patterns, relationships, paths, graph algorithms
- Database theory: ACID, CAP theorem, data modeling, normalization
- Query optimization and performance tuning

CRITICAL RULES FOR ANSWERS:
1. Provide ONLY the final answers - NO explanations, NO reasoning, NO step-by-step
2. For queries: Write complete, syntactically correct queries ready to execute
3. For query outputs: Show exact result format (JSON for MongoDB, tabular for Neo4j)
4. For multiple choice: just state the correct letter/option
5. For true/false: just say "True" or "False"
6. For theoretical questions: Brief, direct answer (maximum 2-3 words when possible)
7. If multiple questions, number them: "1. Answer" "2. Answer" etc.
8. If no questions are found in the image, return exactly: "no questions found"

QUERY FORMAT EXAMPLES:
MongoDB: db.collection.find({field: value})
Neo4j: MATCH (n:Label) RETURN n

MULTIPLE CHOICE FORMAT:
1. B
2. A

OUTPUT EXAMPLES:
MongoDB: [{_id: 1, name: "John", age: 30}]
Neo4j: | name | age |
        | John | 30  |

DO NOT include explanations, reasoning, or steps unless specifically requested via custom instruction."""

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

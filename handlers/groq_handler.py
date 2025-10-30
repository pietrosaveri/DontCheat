import os
import base64
from groq import Groq
from dotenv import load_dotenv

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

QUERY FORMAT EXAMPLES:
MongoDB: db.collection.find({field: value})
Neo4j: MATCH (n:Label) RETURN n

MULTIPLE CHOICE FORMAT:
1. B
2. A

DO NOT include explanations, reasoning, or steps unless specifically requested via custom instruction."""

def analyze_screenshot(image_path, reference_image_path=None):
    """
    Analyze a screenshot using Groq's VLM API.
    
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

from flask import Flask, request, jsonify
from handlers.gemini_handler import analyze_screenshot
import os
import base64
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'screenshots'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

context_image_path = None

@app.route('/')
def home():
    """Home page showing API status and available endpoints"""
    return jsonify({
        'status': 'running',
        'service': 'DontCheat API',
        'endpoints': {
            '/analyze': 'POST - Analyze screenshot with optional context',
            '/clear_context': 'POST - Clear saved context image',
            '/status': 'GET - Check server status'
        },
        'context_loaded': context_image_path is not None
    })

@app.route('/status')
def status():
    """Check if server is running and if context is loaded"""
    return jsonify({
        'status': 'ok',
        'context_loaded': context_image_path is not None,
        'context_path': context_image_path if context_image_path else None
    })

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests to avoid 404 errors"""
    return '', 204

@app.route('/apple-touch-icon.png')
@app.route('/apple-touch-icon-precomposed.png')
def apple_touch_icon():
    """Handle Apple touch icon requests to avoid 404 errors"""
    return '', 204

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """Receive screenshot from iPhone and analyze it"""
    global context_image_path
    
    if request.method == 'GET':
        return jsonify({
            'endpoint': '/analyze',
            'method': 'POST',
            'description': 'Analyze a screenshot with optional context',
            'body': {
                'image': 'base64 encoded image data (required)',
                'is_context': 'boolean - true to save as context, false to analyze (default: false)'
            },
            'example': {
                'image': '<base64_encoded_image>',
                'is_context': False
            }
        })
    
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'status': 'error', 'answer': 'Missing image data in request'}), 400
        
        image_data = base64.b64decode(data['image'])
        is_context = data.get('is_context', False)
        
        # Save the image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(UPLOAD_FOLDER, f"screenshot_{timestamp}.png")
        
        with open(image_path, 'wb') as f:
            f.write(image_data)
        
        if is_context:
            context_image_path = image_path
            return jsonify({'status': 'success', 'answer': 'Context image saved'})
        else:
            # Analyze the screenshot
            answer = analyze_screenshot(image_path, context_image_path)
            return jsonify({'status': 'success', 'answer': answer if answer else 'No answer generated'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'answer': f'Server error: {str(e)}'}), 500

@app.route('/clear_context', methods=['GET', 'POST'])
def clear_context():
    """Clear the saved context"""
    global context_image_path
    
    if request.method == 'GET':
        return jsonify({
            'endpoint': '/clear_context',
            'method': 'POST',
            'description': 'Clear the saved context image',
            'current_context': context_image_path if context_image_path else 'No context loaded'
        })
    
    context_image_path = None
    return jsonify({'status': 'success', 'message': 'Context cleared'})

if __name__ == '__main__':
    # Run on local network so iPhone can access it
    app.run(host='0.0.0.0', port=5001, debug=True)
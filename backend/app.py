from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import requests
from datetime import datetime
import json
import base64
from io import BytesIO
import html2image
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration for NVIDIA Nemotron API
NVIDIA_API_KEY = os.environ.get('NVIDIA_API_KEY', '')
NVIDIA_API_URL = os.environ.get('NVIDIA_API_URL', 'https://integrate.api.nvidia.com/v1/chat/completions')

# Storage for mockups and feedback
MOCKUPS_DIR = Path('mockups')
MOCKUPS_DIR.mkdir(exist_ok=True)
FEEDBACK_FILE = 'feedback.json'

# Initialize html2image
hti = html2image.Html2Image(output_path=str(MOCKUPS_DIR))

def load_feedback():
    """Load feedback from JSON file"""
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_feedback(feedback_data):
    """Save feedback to JSON file"""
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(feedback_data, f, indent=2)

def call_nvidia_nemotron(prompt, system_message):
    """Call NVIDIA Nemotron API"""
    headers = {
        'Authorization': f'Bearer {NVIDIA_API_KEY}',
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
        response = requests.post(NVIDIA_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error calling NVIDIA API: {str(e)}")
        # Fallback to mock response for development
        return generate_mock_html(prompt)

def generate_mock_html(prompt):
    """Generate a simple HTML mockup (fallback for development)"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mockup</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            max-width: 1200px;
            width: 90%;
            background: white;
            border-radius: 20px;
            padding: 60px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #667eea;
            font-size: 3em;
            margin-bottom: 20px;
            text-align: center;
        }}
        p {{
            color: #555;
            font-size: 1.2em;
            line-height: 1.8;
            text-align: center;
            margin-bottom: 30px;
        }}
        .cta-button {{
            display: block;
            width: fit-content;
            margin: 0 auto;
            padding: 15px 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: bold;
            transition: transform 0.3s;
        }}
        .cta-button:hover {{
            transform: translateY(-3px);
        }}
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            margin-top: 50px;
        }}
        .feature-card {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
        }}
        .feature-card h3 {{
            color: #667eea;
            margin-bottom: 15px;
        }}
        .mockup-note {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            padding: 15px;
            border-radius: 10px;
            margin-top: 30px;
            text-align: center;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Your Product Vision</h1>
        <p>Based on your requirements: "{prompt[:100]}..."</p>
        <a href="#" class="cta-button">Get Started</a>
        
        <div class="feature-grid">
            <div class="feature-card">
                <h3>🎯 Feature One</h3>
                <p>Key functionality that addresses user needs</p>
            </div>
            <div class="feature-card">
                <h3>⚡ Feature Two</h3>
                <p>Performance and efficiency optimizations</p>
            </div>
            <div class="feature-card">
                <h3>🔒 Feature Three</h3>
                <p>Security and compliance features</p>
            </div>
        </div>
        
        <div class="mockup-note">
            <strong>📝 Note:</strong> This is an AI-generated mockup for stakeholder review.
            Provide feedback to refine before development.
        </div>
    </div>
</body>
</html>"""

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'PM Mockup Generator API is running'})

@app.route('/api/generate-mockup', methods=['POST'])
def generate_mockup():
    """Generate HTML mockup from prompt using NVIDIA Nemotron"""
    data = request.json
    prompt = data.get('prompt', '')
    project_name = data.get('project_name', 'Untitled Project')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    # Create system message for mockup generation
    system_message = """You are an expert UI/UX designer and frontend developer. Generate complete, production-ready HTML mockups based on user requirements.

Your mockups should:
1. Be fully self-contained with inline CSS (no external dependencies)
2. Use modern, professional design principles
3. Include responsive design
4. Use a cohesive color scheme
5. Include placeholder content that makes sense for the use case
6. Be visually appealing and suitable for stakeholder presentations
7. Include semantic HTML5 elements
8. Use modern CSS features (flexbox, grid, gradients, shadows, etc.)

Return ONLY the complete HTML code, no explanations or markdown formatting."""
    
    # Call NVIDIA Nemotron to generate HTML
    html_content = call_nvidia_nemotron(prompt, system_message)
    
    # Clean up the response (remove thinking tags and markdown code blocks)
    # Remove <think>...</think> sections that the model might include
    if '<think>' in html_content and '</think>' in html_content:
        # Find and remove everything between <think> and </think>
        start_idx = html_content.find('<think>')
        end_idx = html_content.find('</think>') + len('</think>')
        html_content = html_content[:start_idx] + html_content[end_idx:]
        html_content = html_content.strip()
    
    # Remove markdown code blocks if present
    if '```html' in html_content:
        html_content = html_content.split('```html')[1].split('```')[0].strip()
    elif '```' in html_content:
        html_content = html_content.split('```')[1].split('```')[0].strip()
    
    # Generate unique ID for this mockup
    mockup_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save HTML file
    html_filename = f'mockup_{mockup_id}.html'
    html_path = MOCKUPS_DIR / html_filename
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    # Generate screenshot
    screenshot_filename = f'mockup_{mockup_id}.png'
    try:
        hti.screenshot(
            html_str=html_content,
            save_as=screenshot_filename,
            size=(1400, 900)
        )
    except Exception as e:
        print(f"Error generating screenshot: {str(e)}")
        # Continue without screenshot
    
    # Save mockup metadata
    mockup_data = {
        'id': mockup_id,
        'project_name': project_name,
        'prompt': prompt,
        'html_filename': html_filename,
        'screenshot_filename': screenshot_filename,
        'created_at': datetime.now().isoformat(),
        'feedback': []
    }
    
    return jsonify({
        'success': True,
        'mockup': mockup_data,
        'html_content': html_content
    })

@app.route('/api/mockups/<mockup_id>/html', methods=['GET'])
def get_mockup_html(mockup_id):
    """Get HTML content of a mockup"""
    html_path = MOCKUPS_DIR / f'mockup_{mockup_id}.html'
    if html_path.exists():
        return send_file(html_path, mimetype='text/html')
    return jsonify({'error': 'Mockup not found'}), 404

@app.route('/api/mockups/<mockup_id>/screenshot', methods=['GET'])
def get_mockup_screenshot(mockup_id):
    """Get screenshot of a mockup"""
    screenshot_path = MOCKUPS_DIR / f'mockup_{mockup_id}.png'
    if screenshot_path.exists():
        return send_file(screenshot_path, mimetype='image/png')
    return jsonify({'error': 'Screenshot not found'}), 404

@app.route('/api/mockups/<mockup_id>/feedback', methods=['POST'])
def add_feedback(mockup_id):
    """Add feedback to a mockup"""
    data = request.json
    feedback_text = data.get('feedback', '')
    author = data.get('author', 'Anonymous')
    
    if not feedback_text:
        return jsonify({'error': 'Feedback text is required'}), 400
    
    # Load existing feedback
    all_feedback = load_feedback()
    
    if mockup_id not in all_feedback:
        all_feedback[mockup_id] = []
    
    # Add new feedback
    feedback_entry = {
        'id': len(all_feedback[mockup_id]) + 1,
        'author': author,
        'text': feedback_text,
        'timestamp': datetime.now().isoformat()
    }
    
    all_feedback[mockup_id].append(feedback_entry)
    save_feedback(all_feedback)
    
    return jsonify({'success': True, 'feedback': feedback_entry})

@app.route('/api/mockups/<mockup_id>/feedback', methods=['GET'])
def get_feedback(mockup_id):
    """Get all feedback for a mockup"""
    all_feedback = load_feedback()
    mockup_feedback = all_feedback.get(mockup_id, [])
    return jsonify({'feedback': mockup_feedback})

@app.route('/api/refine-mockup', methods=['POST'])
def refine_mockup():
    """Refine an existing mockup based on feedback"""
    data = request.json
    original_html = data.get('original_html', '')
    feedback_list = data.get('feedback', [])
    
    if not original_html or not feedback_list:
        return jsonify({'error': 'Original HTML and feedback are required'}), 400
    
    # Create refinement prompt
    feedback_text = '\n'.join([f"- {fb}" for fb in feedback_list])
    refinement_prompt = f"""Based on the following feedback, refine this HTML mockup:

Feedback:
{feedback_text}

Original HTML:
{original_html}

Please provide an improved version that addresses all the feedback points."""
    
    system_message = """You are an expert UI/UX designer refining mockups based on stakeholder feedback. 
Generate complete, improved HTML that addresses all feedback points while maintaining design quality.
Return ONLY the complete HTML code, no explanations."""
    
    # Call NVIDIA Nemotron to refine
    refined_html = call_nvidia_nemotron(refinement_prompt, system_message)
    
    # Clean up the response (remove thinking tags and markdown code blocks)
    if '<think>' in refined_html and '</think>' in refined_html:
        start_idx = refined_html.find('<think>')
        end_idx = refined_html.find('</think>') + len('</think>')
        refined_html = refined_html[:start_idx] + refined_html[end_idx:]
        refined_html = refined_html.strip()
    
    if '```html' in refined_html:
        refined_html = refined_html.split('```html')[1].split('```')[0].strip()
    elif '```' in refined_html:
        refined_html = refined_html.split('```')[1].split('```')[0].strip()
    
    # Generate new mockup ID
    mockup_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save refined HTML
    html_filename = f'mockup_{mockup_id}.html'
    html_path = MOCKUPS_DIR / html_filename
    with open(html_path, 'w') as f:
        f.write(refined_html)
    
    # Generate screenshot
    screenshot_filename = f'mockup_{mockup_id}.png'
    try:
        hti.screenshot(
            html_str=refined_html,
            save_as=screenshot_filename,
            size=(1400, 900)
        )
    except Exception as e:
        print(f"Error generating screenshot: {str(e)}")
    
    return jsonify({
        'success': True,
        'mockup_id': mockup_id,
        'html_content': refined_html
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')


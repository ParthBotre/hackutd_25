from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import requests
from datetime import datetime
import html2image
from pathlib import Path
from dotenv import load_dotenv
import sqlite3
import uuid
import json

# Load environment variables from .env file
# Try to load from backend directory explicitly
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
# Also try default location
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration for NVIDIA Nemotron API
NVIDIA_API_KEY = os.environ.get('NVIDIA_API_KEY', '').strip()
NVIDIA_API_URL = os.environ.get('NVIDIA_API_URL', 'https://integrate.api.nvidia.com/v1/chat/completions').strip()

# Debug: Check if API key is loaded (don't print the actual key)
if NVIDIA_API_KEY:
    print(f"[OK] NVIDIA_API_KEY loaded (length: {len(NVIDIA_API_KEY)} characters)")
else:
    print("[WARNING] NVIDIA_API_KEY is empty or not set")

# Storage directories and database
MOCKUPS_DIR = Path('mockups')
MOCKUPS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = Path('data')
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / 'mockups.db'

# Initialize html2image
hti = html2image.Html2Image(output_path=str(MOCKUPS_DIR))

# In-memory storage for chat conversations
# In production, this should be stored in a database
chat_conversations = {}

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mockups (
                    id TEXT PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    html_content TEXT NOT NULL,
                    html_filename TEXT NOT NULL,
                    screenshot_filename TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mockup_id TEXT NOT NULL,
                    author TEXT NOT NULL,
                    text TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(mockup_id) REFERENCES mockups(id) ON DELETE CASCADE
                )
                """
            )
    finally:
        conn.close()

def save_mockup_to_db(mockup_data, html_content):
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO mockups (
                    id, project_name, prompt, html_content,
                    html_filename, screenshot_filename, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mockup_data['id'],
                    mockup_data['project_name'],
                    mockup_data['prompt'],
                    html_content,
                    mockup_data['html_filename'],
                    mockup_data['screenshot_filename'],
                    mockup_data['created_at']
                )
            )
    finally:
        conn.close()

def get_mockup_from_db(mockup_id):
    conn = get_db_connection()
    try:
        mockup = conn.execute(
            "SELECT * FROM mockups WHERE id = ?",
            (mockup_id,)
        ).fetchone()
    finally:
        conn.close()
    return mockup

def list_mockups_from_db(limit=None, include_html=False):
    conn = get_db_connection()
    try:
        query = "SELECT * FROM mockups ORDER BY datetime(created_at) DESC"
        if limit is not None:
            query += " LIMIT ?"
            rows = conn.execute(query, (limit,)).fetchall()
        else:
            rows = conn.execute(query).fetchall()
    finally:
        conn.close()
    return [
        {
            'id': row['id'],
            'project_name': row['project_name'],
            'prompt': row['prompt'],
            'created_at': row['created_at'],
            'html_filename': row['html_filename'],
            'screenshot_filename': row['screenshot_filename'],
            **({'html_content': row['html_content']} if include_html else {})
        }
        for row in rows
    ]

def get_feedback_from_db(mockup_id):
    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, author, text, timestamp
            FROM feedback
            WHERE mockup_id = ?
            ORDER BY timestamp ASC
            """,
            (mockup_id,)
        ).fetchall()
    finally:
        conn.close()
    return [
        {
            'id': row['id'],
            'author': row['author'],
            'text': row['text'],
            'timestamp': row['timestamp']
        }
        for row in rows
    ]

def add_feedback_to_db(mockup_id, author, feedback_text):
    conn = get_db_connection()
    timestamp = datetime.now().isoformat()
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO feedback (mockup_id, author, text, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (
                    mockup_id,
                    author,
                    feedback_text,
                    timestamp
                )
            )
            feedback_id = cursor.lastrowid
    finally:
        conn.close()
    return {
        'id': feedback_id,
        'author': author,
        'text': feedback_text,
        'timestamp': timestamp
    }

init_db()

def serialize_mockup_row(row, include_html=False):
    mockup = {
        'id': row['id'],
        'project_name': row['project_name'],
        'prompt': row['prompt'],
        'created_at': row['created_at'],
        'html_filename': row['html_filename'],
        'screenshot_filename': row['screenshot_filename']
    }
    if include_html:
        mockup['html_content'] = row['html_content']
    return mockup

from nemotron_client import call_nvidia_nemotron

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

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and manage conversation"""
    try:
        data = request.json
        message = data.get('message', '')
        conversation_id = data.get('conversation_id')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Generate or use existing conversation ID
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Initialize conversation if new
        if conversation_id not in chat_conversations:
            chat_conversations[conversation_id] = {
                'messages': [],
                'ready_to_generate': False,
                'project_info': {}
            }
        
        conversation = chat_conversations[conversation_id]
        
        # Add user message to conversation history
        conversation['messages'].append({
            'role': 'user',
            'content': message
        })
        
        # Create system prompt for the AI assistant
        system_message = """You are a Product Manager assistant helping to gather requirements for mockup generation.

Your goal is to understand the user's product vision through conversation. Ask clarifying questions about:
- Target audience and user personas
- Key features and functionality
- Design preferences (colors, style, layout)
- User flow and interactions
- Any specific content or branding requirements

When you have gathered enough information to create a comprehensive mockup, include the special tag <READY_TO_GENERATE> in your response with a complete summary of the requirements.

Be conversational, friendly, and ask one or two questions at a time to avoid overwhelming the user."""

        # Prepare conversation history for the AI
        conversation_history = []
        for msg in conversation['messages'][:-1]:  # All messages except the current one
            conversation_history.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # Call NVIDIA Nemotron for response
        ai_response = call_nvidia_nemotron(message, system_message, conversation_history)
        
        # Add AI response to conversation
        conversation['messages'].append({
            'role': 'assistant',
            'content': ai_response
        })
        
        # Check if AI is ready to generate mockup
        ready_to_generate = '<READY_TO_GENERATE>' in ai_response and '</READY_TO_GENERATE>' in ai_response
        
        # If ready to generate, extract the summary and generate mockup
        mockup_data = None
        html_content = None
        
        if ready_to_generate:
            # Extract the summary between tags
            start_tag = '<READY_TO_GENERATE>'
            end_tag = '</READY_TO_GENERATE>'
            start_idx = ai_response.find(start_tag) + len(start_tag)
            end_idx = ai_response.find(end_tag)
            summary = ai_response[start_idx:end_idx].strip()
            
            # Generate mockup using the summary as prompt
            system_message_mockup = """You are an expert UI/UX designer and frontend developer. Generate complete, production-ready HTML mockups based on user requirements.

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
            
            html_content = call_nvidia_nemotron(summary, system_message_mockup, [])
            
            # Clean up the HTML response
            if '<think>' in html_content and '</think>' in html_content:
                start_idx = html_content.find('<think>')
                end_idx = html_content.find('</think>') + len('</think>')
                html_content = html_content[:start_idx] + html_content[end_idx:]
                html_content = html_content.strip()
            
            if '```html' in html_content:
                html_content = html_content.split('```html')[1].split('```')[0].strip()
            elif '```' in html_content:
                html_content = html_content.split('```')[1].split('```')[0].strip()
            
            # Generate mockup metadata
            mockup_id = datetime.now().strftime('%Y%m%d_%H%M%S%f')
            created_at = datetime.now().isoformat()
            
            # Save HTML file
            html_filename = f'mockup_{mockup_id}.html'
            html_path = MOCKUPS_DIR / html_filename
            with open(html_path, 'w', encoding='utf-8') as f:
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
            
            # Create mockup data
            mockup_data = {
                'id': mockup_id,
                'project_name': f"Chat Project {mockup_id}",
                'prompt': summary,
                'html_filename': html_filename,
                'screenshot_filename': screenshot_filename,
                'created_at': created_at,
                'feedback': []
            }
            
            # Save to database
            save_mockup_to_db(mockup_data, html_content)
            
            conversation['ready_to_generate'] = True
            conversation['mockup_id'] = mockup_id
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'message': ai_response,
            'ready_to_generate': ready_to_generate,
            'mockup': mockup_data,
            'html_content': html_content
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get conversation history"""
    if conversation_id not in chat_conversations:
        return jsonify({'error': 'Conversation not found'}), 404
    
    return jsonify({
        'conversation_id': conversation_id,
        'messages': chat_conversations[conversation_id]['messages'],
        'ready_to_generate': chat_conversations[conversation_id]['ready_to_generate']
    })

@app.route('/api/debug/api-key', methods=['GET'])
def debug_api_key():
    """Debug endpoint to check API key status (without exposing the key)"""
    api_key_set = bool(NVIDIA_API_KEY and NVIDIA_API_KEY.strip())
    api_key_length = len(NVIDIA_API_KEY.strip()) if NVIDIA_API_KEY else 0
    api_key_preview = f"{NVIDIA_API_KEY[:8]}..." if api_key_set and len(NVIDIA_API_KEY) > 8 else "Not set"
    
    return jsonify({
        'api_key_set': api_key_set,
        'api_key_length': api_key_length,
        'api_key_preview': api_key_preview,
        'api_url': NVIDIA_API_URL
    })

@app.route('/api/mockups', methods=['GET'])
def list_mockups():
    """List stored mockups"""
    limit_param = request.args.get('limit')
    include_html = request.args.get('include_html', 'false').lower() == 'true'

    if limit_param is not None:
        try:
            limit = int(limit_param)
        except ValueError:
            return jsonify({'error': 'Limit must be an integer'}), 400
        if limit <= 0:
            return jsonify({'error': 'Limit must be positive'}), 400
    else:
        limit = None

    mockups = list_mockups_from_db(limit=limit, include_html=include_html)
    return jsonify({'mockups': mockups})

@app.route('/api/mockups/<mockup_id>', methods=['GET'])
def get_mockup(mockup_id):
    """Retrieve metadata (and optionally HTML) for a single mockup"""
    include_html = request.args.get('include_html', 'true').lower() == 'true'
    row = get_mockup_from_db(mockup_id)
    if not row:
        return jsonify({'error': 'Mockup not found'}), 404
    mockup = serialize_mockup_row(row, include_html=include_html)
    mockup['feedback'] = get_feedback_from_db(mockup_id)
    return jsonify({'mockup': mockup})

@app.route('/api/generate-mockup', methods=['POST'])
def generate_mockup():
    """Generate HTML mockup from prompt using NVIDIA Nemotron"""
    data = request.json
    prompt = data.get('prompt', '')
    project_name = data.get('project_name', 'Untitled Project')
    github_repo_url = data.get('github_repo_url', '') or os.environ.get('GITHUB_REPO_URL', '')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    # If GitHub repo URL is provided, use repo-aware generator to enhance with repo context
    if github_repo_url:
        try:
            from repo_mockup_generator import generate_mockup_from_repo
            print(f"Using GitHub repository context: {github_repo_url}")
            html_content = generate_mockup_from_repo(github_repo_url, prompt, None)
        except Exception as e:
            print(f"Error using GitHub repo context: {str(e)}")
            import traceback
            traceback.print_exc()
            print("Falling back to standard mockup generation")
            # Fall back to standard generation
            github_repo_url = None
    
    # Standard mockup generation (if no GitHub repo or if GitHub integration failed)
    if not github_repo_url:
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
    mockup_id = datetime.now().strftime('%Y%m%d_%H%M%S%f')
    created_at = datetime.now().isoformat()
    
    # Save HTML file
    html_filename = f'mockup_{mockup_id}.html'
    html_path = MOCKUPS_DIR / html_filename
    with open(html_path, 'w', encoding='utf-8') as f:
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
    
    # Save mockup metadata (include GitHub repo URL if used)
    mockup_data = {
        'id': mockup_id,
        'project_name': project_name,
        'prompt': prompt,
        'html_filename': html_filename,
        'screenshot_filename': screenshot_filename,
        'created_at': created_at,
        'feedback': [],
        'github_repo_url': github_repo_url if github_repo_url else None
    }

    save_mockup_to_db(mockup_data, html_content)
    
    return jsonify({
        'success': True,
        'mockup': mockup_data,
        'html_content': html_content,
        'used_github_context': bool(github_repo_url)
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
    
    if not get_mockup_from_db(mockup_id):
        return jsonify({'error': 'Mockup not found'}), 404
    
    feedback_entry = add_feedback_to_db(mockup_id, author, feedback_text)
    
    return jsonify({'success': True, 'feedback': feedback_entry})

@app.route('/api/mockups/<mockup_id>/feedback', methods=['GET'])
def get_feedback(mockup_id):
    """Get all feedback for a mockup"""
    if not get_mockup_from_db(mockup_id):
        return jsonify({'error': 'Mockup not found'}), 404
    mockup_feedback = get_feedback_from_db(mockup_id)
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
    mockup_id = datetime.now().strftime('%Y%m%d_%H%M%S%f')
    created_at = datetime.now().isoformat()
    
    # Save refined HTML
    html_filename = f'mockup_{mockup_id}.html'
    html_path = MOCKUPS_DIR / html_filename
    with open(html_path, 'w', encoding='utf-8') as f:
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
    
    refined_mockup_data = {
        'id': mockup_id,
        'project_name': 'Refined Mockup',
        'prompt': refinement_prompt,
        'html_filename': html_filename,
        'screenshot_filename': screenshot_filename,
        'created_at': created_at,
        'feedback': []
    }

    save_mockup_to_db(refined_mockup_data, refined_html)

    return jsonify({
        'success': True,
        'mockup_id': mockup_id,
        'html_content': refined_html
    })

@app.route('/api/edit-html', methods=['POST'])
def edit_html():
    """Edit HTML using natural language instructions"""
    data = request.json
    original_html = data.get('html_content', '')
    edit_instruction = data.get('instruction', '')
    
    if not original_html or not edit_instruction:
        return jsonify({'error': 'HTML content and edit instruction are required'}), 400
    
    # Create edit prompt
    edit_prompt = f"""Edit the following HTML according to this instruction: {edit_instruction}

Original HTML:
{original_html}

Please provide the complete modified HTML code that implements the requested changes. Return ONLY the complete HTML code, no explanations or markdown formatting."""
    
    system_message = """You are an expert frontend developer and HTML editor. 
When given HTML code and an edit instruction, modify the HTML to implement the requested changes.
Maintain the overall structure and styling while making the specific requested modifications.
Return ONLY the complete HTML code, no explanations."""
    
    try:
        # Call NVIDIA Nemotron to edit
        edited_html = call_nvidia_nemotron(edit_prompt, system_message)
        
        # Clean up the response (remove thinking tags and markdown code blocks)
        if '<think>' in edited_html and '</think>' in edited_html:
            start_idx = edited_html.find('<think>')
            end_idx = edited_html.find('</think>') + len('</think>')
            edited_html = edited_html[:start_idx] + edited_html[end_idx:]
            edited_html = edited_html.strip()
        
        if '```html' in edited_html:
            edited_html = edited_html.split('```html')[1].split('```')[0].strip()
        elif '```' in edited_html:
            edited_html = edited_html.split('```')[1].split('```')[0].strip()
        
        return jsonify({
            'success': True,
            'html_content': edited_html
        })
    except Exception as e:
        print(f"Error in edit_html endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mockups/<mockup_id>/update', methods=['PUT'])
def update_mockup_html(mockup_id):
    """Update the HTML content of an existing mockup"""
    data = request.json
    new_html = data.get('html_content', '')
    
    if not new_html:
        return jsonify({'error': 'HTML content is required'}), 400
    
    mockup = get_mockup_from_db(mockup_id)
    if not mockup:
        return jsonify({'error': 'Mockup not found'}), 404
    
    # Update HTML in database
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                "UPDATE mockups SET html_content = ? WHERE id = ?",
                (new_html, mockup_id)
            )
    finally:
        conn.close()
    
    # Update HTML file
    html_path = MOCKUPS_DIR / f'mockup_{mockup_id}.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    # Regenerate screenshot
    screenshot_filename = f'mockup_{mockup_id}.png'
    try:
        hti.screenshot(
            html_str=new_html,
            save_as=screenshot_filename,
            size=(1400, 900)
        )
    except Exception as e:
        print(f"Error generating screenshot: {str(e)}")
    
    return jsonify({
        'success': True,
        'message': 'Mockup updated successfully'
    })

@app.route('/api/jira/test', methods=['GET'])
def test_jira_connection_endpoint():
    """Test Jira connection and return status"""
    try:
        from jira_integration import test_jira_connection
        result = test_jira_connection()
        
        if result["connected"]:
            return jsonify({
                'success': True,
                'connected': True,
                'user': result.get('user'),
                'base_url': result['base_url']
            })
        else:
            return jsonify({
                'success': False,
                'connected': False,
                'error': result.get('error'),
                'email_configured': result['email_configured'],
                'token_configured': result['token_configured']
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'connected': False,
            'error': str(e)
        }), 500

@app.route('/api/jira/tickets', methods=['GET'])
def get_jira_tickets():
    """Get all JIRA tickets from the board"""
    try:
        from jira_integration import get_board_issues, validate_jira_credentials
        
        if not validate_jira_credentials():
            return jsonify({
                'success': False,
                'error': 'JIRA credentials not configured or invalid'
            }), 401
        
        # Get board_id from query params, default to 1
        board_id = request.args.get('board_id', 1, type=int)
        
        tickets = get_board_issues(board_id=board_id)
        
        # Format tickets for frontend
        formatted_tickets = []
        for ticket in tickets:
            fields = ticket.get('fields', {})
            formatted_tickets.append({
                'key': ticket.get('key'),
                'id': ticket.get('id'),
                'summary': fields.get('summary', ''),
                'status': fields.get('status', {}).get('name', 'Unknown'),
                'statusCategory': fields.get('status', {}).get('statusCategory', {}).get('key', 'todo'),
                'issueType': fields.get('issuetype', {}).get('name', 'Task'),
                'issueTypeIcon': fields.get('issuetype', {}).get('iconUrl', ''),
                'priority': fields.get('priority', {}).get('name', 'Medium') if fields.get('priority') else 'Medium',
                'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                'assigneeAvatar': fields.get('assignee', {}).get('avatarUrls', {}).get('48x48', '') if fields.get('assignee') else '',
                'created': fields.get('created', ''),
                'updated': fields.get('updated', ''),
                'url': f"{os.environ.get('JIRA_BASE_URL', 'https://hack-utd-automations.atlassian.net')}/browse/{ticket.get('key')}"
            })
        
        return jsonify({
            'success': True,
            'tickets': formatted_tickets,
            'count': len(formatted_tickets)
        })
    
    except Exception as e:
        print(f"Error fetching JIRA tickets: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/jira/tickets/<ticket_key>', methods=['GET'])
def get_jira_ticket_detail(ticket_key):
    """Get detailed information about a specific JIRA ticket"""
    try:
        from jira_integration import validate_jira_credentials
        import requests
        from requests.auth import HTTPBasicAuth
        
        if not validate_jira_credentials():
            return jsonify({
                'success': False,
                'error': 'JIRA credentials not configured or invalid'
            }), 401
        
        # Get JIRA credentials
        JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "https://hack-utd-automations.atlassian.net")
        JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
        JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
        
        auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        # Fetch ticket details
        response = requests.get(
            f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_key}",
            headers=headers,
            auth=auth,
            verify=False,
            timeout=30
        )
        response.raise_for_status()
        ticket = response.json()
        
        fields = ticket.get('fields', {})
        
        # Format ticket detail
        formatted_ticket = {
            'key': ticket.get('key'),
            'id': ticket.get('id'),
            'summary': fields.get('summary', ''),
            'description': fields.get('description', {}),
            'status': fields.get('status', {}).get('name', 'Unknown'),
            'statusCategory': fields.get('status', {}).get('statusCategory', {}).get('key', 'todo'),
            'issueType': fields.get('issuetype', {}).get('name', 'Task'),
            'issueTypeIcon': fields.get('issuetype', {}).get('iconUrl', ''),
            'priority': fields.get('priority', {}).get('name', 'Medium') if fields.get('priority') else 'Medium',
            'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
            'assigneeAvatar': fields.get('assignee', {}).get('avatarUrls', {}).get('48x48', '') if fields.get('assignee') else '',
            'reporter': fields.get('reporter', {}).get('displayName', 'Unknown') if fields.get('reporter') else 'Unknown',
            'created': fields.get('created', ''),
            'updated': fields.get('updated', ''),
            'url': f"{JIRA_BASE_URL}/browse/{ticket.get('key')}"
        }
        
        return jsonify({
            'success': True,
            'ticket': formatted_ticket
        })
    
    except Exception as e:
        print(f"Error fetching JIRA ticket detail: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/<conversation_id>/create-tickets', methods=['POST'])
def create_tickets_from_chat(conversation_id):
    """Create JIRA tickets from a chat conversation mockup"""
    try:
        if conversation_id not in chat_conversations:
            return jsonify({'error': 'Conversation not found'}), 404
        
        conversation = chat_conversations[conversation_id]
        
        if not conversation.get('mockup_id'):
            return jsonify({'error': 'No mockup generated yet in this conversation'}), 400
        
        mockup_id = conversation['mockup_id']
        
        # Get mockup data from database
        mockup = get_mockup_from_db(mockup_id)
        if not mockup:
            return jsonify({'error': 'Mockup not found'}), 404
        
        # Get GitHub repo URL from request or environment
        data = request.get_json(silent=True) or {}
        github_repo_url = data.get('github_repo_url') or os.environ.get('GITHUB_REPO_URL', '')
        
        if not github_repo_url:
            return jsonify({
                'error': 'GitHub repository URL is required for ticket generation'
            }), 400
        
        # Get HTML content
        html_path = MOCKUPS_DIR / mockup['html_filename']
        if not html_path.exists():
            return jsonify({'error': 'Mockup HTML file not found'}), 404
        
        with open(html_path, 'r', encoding='utf-8') as f:
            mockup_html = f.read()
        
        # Analyze repository and create tickets
        from repo_mockup_generator import parse_github_url
        from github_integration import analyze_repo_for_mockup
        from mockup_analyzer import analyze_mockup_vs_repo, create_tickets_from_analysis
        
        owner, repo_name = parse_github_url(github_repo_url)
        if not owner or not repo_name:
            return jsonify({'error': 'Invalid GitHub repository URL'}), 400
        
        print(f"Analyzing repository {owner}/{repo_name} for comparison with mockup")
        
        # Get repository data
        repo_data = analyze_repo_for_mockup(owner, repo_name, mockup['prompt'], None)
        
        # Analyze differences and create tickets
        print("Analyzing mockup vs repository to create tickets...")
        tickets = analyze_mockup_vs_repo(mockup_html, repo_data, github_repo_url)
        
        print(f"Generated {len(tickets)} tickets from analysis")
        
        # Create tickets in Jira
        results = create_tickets_from_analysis(tickets, github_repo_url, mockup_id)
        
        # Count successes and failures
        successful = [r for r in results if r.get('success')]
        failed = [r for r in results if not r.get('success')]
        
        return jsonify({
            'success': True,
            'message': f'Created {len(successful)} ticket(s) in Jira',
            'tickets_created': len(successful),
            'tickets_failed': len(failed),
            'tickets': [
                {
                    'title': r.get('title', 'Unknown'),
                    'issue_key': r.get('issue_key'),
                    'issue_url': r.get('issue_url'),
                    'difficulty': r.get('difficulty'),
                    'priority': r.get('priority'),
                    'success': r.get('success', False),
                    'error': r.get('error') if not r.get('success') else None
                }
                for r in results
            ]
        })
    
    except Exception as e:
        print(f"Error creating tickets from chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/mockups/<mockup_id>/submit', methods=['POST'])
def submit_mockup_to_jira(mockup_id):
    """Submit mockup to Jira - analyzes mockup vs repo and creates multiple tickets"""
    try:
        # Get mockup data from database
        mockup = get_mockup_from_db(mockup_id)
        if not mockup:
            return jsonify({'error': 'Mockup not found'}), 404
        
        # Get HTML content
        html_path = MOCKUPS_DIR / mockup['html_filename']
        if not html_path.exists():
            return jsonify({'error': 'Mockup HTML file not found'}), 404
        
        with open(html_path, 'r', encoding='utf-8') as f:
            mockup_html = f.read()
        
        # Get GitHub repo URL from mockup data or request
        # Handle case where request might not have JSON body
        try:
            request_data = request.get_json(silent=True) or {}
        except Exception:
            request_data = {}
        
        # Try to get GitHub URL from request, mockup data, or environment
        github_repo_url = (
            request_data.get('github_repo_url') or 
            mockup.get('github_repo_url') or 
            os.environ.get('GITHUB_REPO_URL', '')
        )
        
        if not github_repo_url:
            return jsonify({
                'error': 'GitHub repository URL is required for ticket generation'
            }), 400
        
        # Re-analyze repository to get current state
        from repo_mockup_generator import parse_github_url
        from github_integration import analyze_repo_for_mockup
        from mockup_analyzer import analyze_mockup_vs_repo, create_tickets_from_analysis
        
        owner, repo_name = parse_github_url(github_repo_url)
        if not owner or not repo_name:
            return jsonify({'error': 'Invalid GitHub repository URL'}), 400
        
        print(f"Analyzing repository {owner}/{repo_name} for comparison with mockup")
        
        # Get repository data
        repo_data = analyze_repo_for_mockup(owner, repo_name, mockup['prompt'], None)
        
        # Analyze differences and create tickets
        print("Analyzing mockup vs repository to create tickets...")
        tickets = analyze_mockup_vs_repo(mockup_html, repo_data, github_repo_url)
        
        print(f"Generated {len(tickets)} tickets from analysis")
        
        # Create tickets in Jira
        results = create_tickets_from_analysis(tickets, github_repo_url, mockup_id)
        
        # Count successes and failures
        successful = [r for r in results if r.get('success')]
        failed = [r for r in results if not r.get('success')]
        
        return jsonify({
            'success': True,
            'message': f'Created {len(successful)} ticket(s) in Jira',
            'tickets_created': len(successful),
            'tickets_failed': len(failed),
            'tickets': [
                {
                    'title': r.get('title', 'Unknown'),
                    'issue_key': r.get('issue_key'),
                    'issue_url': r.get('issue_url'),
                    'difficulty': r.get('difficulty'),
                    'priority': r.get('priority'),
                    'success': r.get('success', False),
                    'error': r.get('error') if not r.get('success') else None
                }
                for r in results
            ]
        })
            
    except ValueError as e:
        error_msg = f'Configuration error: {str(e)}'
        print(f"Jira Configuration Error: {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500
    except Exception as e:
        import traceback
        error_msg = f'Failed to submit mockup to Jira: {str(e)}'
        print(f"Error submitting mockup to Jira: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')


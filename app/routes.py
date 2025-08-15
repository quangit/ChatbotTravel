from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import base64
from config import Config
from app.ai_agent import TravelAIAgent
from app.tts_service import TTSService
from app.models import ChromaDBManager, DocumentProcessor

main = Blueprint('main', __name__)

# Initialize services
ai_agent = TravelAIAgent()
tts_service = TTSService()
db_manager = ChromaDBManager()
doc_processor = DocumentProcessor()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@main.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

@main.route('/admin')
def admin_login():
    """Admin login page"""
    if session.get('admin_logged_in'):
        return render_template('admin.html')
    return render_template('admin_login.html')

@main.route('/admin/login', methods=['POST'])
def admin_authenticate():
    """Authenticate admin user"""
    password = request.form.get('password')
    
    if password == Config.ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        return redirect(url_for('main.admin_login'))
    else:
        flash('Sai mật khẩu!', 'error')
        return render_template('admin_login.html')

@main.route('/admin/logout')
def admin_logout():
    """Logout admin user"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('main.index'))

@main.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.get_json()
        print(f"[DEBUG] Received data: {data}")  # Debug log
        
        if not data:
            print("[DEBUG] No data provided")
            return jsonify({'error': 'No data provided'}), 400
        
        message = data.get('message', '')
        image_data = data.get('image_data')
        image_type = data.get('image_type')
        
        print(f"[DEBUG] Message: {message[:50] if message else 'None'}...")
        print(f"[DEBUG] Has image: {bool(image_data)}")
        
        if not message and not image_data:
            print("[DEBUG] No message or image provided")
            return jsonify({'error': 'Message or image is required'}), 400
        
        # Process query with AI agent
        response = ai_agent.process_query(message, image_data)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"[ERROR] Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Xin lỗi, đã có lỗi xảy ra: {str(e)}',
            'status': 'error'
        }), 500

@main.route('/api/tts', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        print(f"[TTS] Received text: {text}")  # Debug log
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate audio
        audio_data = tts_service.text_to_speech(text)
        
        if audio_data:
            # Convert to base64 for JSON response
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            print(f"[TTS] Generated {len(audio_data)} bytes audio")
            return jsonify({
                'success': True,
                'audio': audio_base64
            })
        else:
            print("[TTS] Failed to generate audio")
            return jsonify({
                'success': False,
                'error': 'Failed to generate audio'
            }), 500
            
    except Exception as e:
        print(f"[TTS] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'TTS Error: {str(e)}'
        }), 500

@main.route('/api/upload', methods=['POST'])
def upload_document():
    """Upload and process documents for admin"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Process document based on file type
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        if file_ext == 'txt':
            chunks = doc_processor.process_text_file(file_path)
        elif file_ext == 'pdf':
            chunks = doc_processor.process_pdf_file(file_path)
        elif file_ext == 'docx':
            chunks = doc_processor.process_docx_file(file_path)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400
        
        if not chunks:
            return jsonify({'error': 'Failed to extract text from file'}), 500
        
        # Add chunks to ChromaDB
        metadatas = [{'source': filename, 'chunk_id': i} for i in range(len(chunks))]
        
        success = db_manager.add_documents(chunks, metadatas)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        if success:
            return jsonify({
                'message': f'Successfully processed {len(chunks)} chunks from {filename}',
                'status': 'success'
            })
        else:
            return jsonify({'error': 'Failed to add documents to database'}), 500
            
    except Exception as e:
        return jsonify({
            'error': f'Upload Error: {str(e)}',
            'status': 'error'
        }), 500

@main.route('/api/image_upload', methods=['POST'])
def upload_image():
    """Handle image upload from chat interface"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Read and encode image
        image_data = file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        return jsonify({
            'image_data': image_base64,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Image upload error: {str(e)}',
            'status': 'error'
        }), 500

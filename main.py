from flask import Flask, render_template, request, jsonify, session, send_file
from src.chat import ChatBot
from src.qbank import QuestionBank
from src.notes import NotesManager
from src.generator import PDFGenerator
from dotenv import load_dotenv
import io
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key-here")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize services
chatbot = ChatBot(api_key=os.getenv("GROQ_API_KEY"))
qbank = QuestionBank(mongo_uri=os.getenv("MONGO_URI"))
pdf_generator = PDFGenerator()
notes_manager = NotesManager(mongo_uri=os.getenv("MONGO_URI"))

# Main routes
@app.route('/')
def home():
    return render_template('index.html', active_page='chat')

@app.route('/qbank')
def qbank_page():
    topics = qbank.get_topics()
    return render_template('qbank.html', active_page='qbank', topics=topics)

@app.route('/pdfqa')
def pdfqa():
    return render_template('pdfqa.html', active_page='pdfqa')

# Authentication routes
@app.route('/auth/status')
def auth_status():
    username = session.get('username')
    return jsonify({
        'logged_in': username is not None,
        'username': username
    })

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        success = notes_manager.login_user(username, password)
        if success:
            session['username'] = username
            return jsonify({'message': 'Login successful', 'username': username})
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'success'})

# Notes routes
@app.route('/notes')
def get_user_notes():
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        notes = notes_manager.get_notes(username)
        return jsonify({'notes': notes})
    except Exception as e:
        logger.error(f"Error getting notes: {str(e)}")
        return jsonify({'error': 'Failed to fetch notes'}), 500

@app.route('/notes', methods=['POST'])
def save_note():
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        content = request.json.get('content')
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        notes_manager.save_note(username, content)
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error saving note: {str(e)}")
        return jsonify({'error': 'Failed to save note'}), 500

@app.route('/notes/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        notes_manager.delete_note(note_id, username)
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error deleting note: {str(e)}")
        return jsonify({'error': 'Failed to delete note'}), 500

@app.route('/notes/download')
def download_notes():
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        notes = notes_manager.get_notes(username)
        
        # Create text file content
        output = io.StringIO()
        output.write(f"Notes for {username}\n")
        output.write(f"Downloaded on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write("-" * 50 + "\n\n")
        
        for note in notes:
            output.write(f"Date: {note['created_at'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            output.write(f"Content: {note['content']}\n")
            output.write("-" * 50 + "\n\n")
        
        # Convert to bytes for sending file
        bytes_io = io.BytesIO(output.getvalue().encode('utf-8'))
        bytes_io.seek(0)
        
        return send_file(
            bytes_io,
            mimetype='text/plain',
            as_attachment=True,
            download_name=f'notes_{username}_{datetime.now().strftime("%Y%m%d")}.txt'
        )
            
    except Exception as e:
        logger.error(f"Error downloading notes: {str(e)}")
        return jsonify({'error': 'Failed to download notes'}), 500

# Chat routes
@app.route('/chat-init', methods=['POST'])
def chat_init():
    try:
        history = chatbot.initialize_chat()
        return jsonify({'history': history})
    except Exception as e:
        logger.error(f"Error initializing chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        response = chatbot.get_response(user_message)
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

# PDF Question Generation routes
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload a PDF'}), 400

        file_content = io.BytesIO(file.read())
        qa_pairs = pdf_generator.process_pdf_from_buffer(file_content)
        
        formatted_qa = [{'question': q, 'answer': a} for q, a in qa_pairs]
        return jsonify({'status': 'success', 'data': formatted_qa})

    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Question Bank routes
@app.route('/questions/<topic>')
def get_questions(topic):
    try:
        page = int(request.args.get('page', 1))
        return jsonify(qbank.get_questions(topic, page))
    except Exception as e:
        logger.error(f"Error getting questions: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
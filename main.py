from flask import Flask, render_template, request, jsonify
from src.chat import ChatBot
from src.qbank import QuestionBank
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from src.generator import PDFGenerator
import io
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key-here")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Initialize services
chatbot = ChatBot(api_key=os.getenv("GROQ_API_KEY"))
qbank = QuestionBank(mongo_uri=os.getenv("MONGO_URI"))
pdf_generator = PDFGenerator()  

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

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        logger.info("Received upload request")
        
        # Check if file was submitted
        if 'file' not in request.files:
            logger.error("No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        logger.info(f"Received file: {file.filename}")
        
        # Check if a file was selected
        if file.filename == '':
            logger.error("No file selected")
            return jsonify({'error': 'No file selected'}), 400
            
        # Validate file type
        if not allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type. Please upload a PDF'}), 400

        # Read file into memory
        logger.info("Reading file into memory")
        file_content = io.BytesIO(file.read())
        
        # Process the PDF and generate Q&A pairs
        logger.info("Processing PDF and generating Q&A pairs")
        qa_pairs = pdf_generator.process_pdf_from_buffer(file_content)
        
        # Format the response
        formatted_qa = []
        for question, answer in qa_pairs:
            formatted_qa.append({
                'question': question,
                'answer': answer
            })
        
        logger.info(f"Successfully generated {len(formatted_qa)} Q&A pairs")
        return jsonify({
            'status': 'success',
            'data': formatted_qa
        })

    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# Chat routes
@app.route('/chat-init', methods=['POST'])
def chat_init():
    history = chatbot.initialize_chat()
    return jsonify({'history': history})

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        response = chatbot.get_response(user_message)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Question Bank routes
@app.route('/questions/<topic>')
def get_questions(topic):
    page = int(request.args.get('page', 1))
    try:
        return jsonify(qbank.get_questions(topic, page))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
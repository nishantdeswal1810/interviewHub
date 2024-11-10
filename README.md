# Interview Hub

A comprehensive web application designed to help users prepare for interviews through interactive chat, question bank access, and PDF-based Q&A generation.


## 🌟 Features

### 1. Interactive Chat (AI-Powered)
- Real-time conversation with an AI assistant
- Context-aware responses for interview preparation
- Supports multiple domains
- Powered by Groq AI API

### 2. Question Bank (Q-Bank)
- Categorized interview questions
- Comprehensive answers and explanations
- Topics include:
  - Python Programming
  - Object-Oriented Programming (OOPs)
  - Machine Learning (ML)
  - Data Structures & Algorithms (DSA)
  - And more...

### 3. PDF Question Generator
- Upload PDF documents to automatically generate Q&A pairs
- Extracts relevant information and creates practice questions
- Ideal for studying from documentation or research papers

### 4. Notes System
- Personal note-taking functionality
- Notes are associated with usernames and passwords
- Persistent storage using MongoDB
- Access notes across all pages
- Downoad notes in .txt format with dates.

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MongoDB
- **AI Integration**: Groq API
- **PDF Processing**: Custom PDF processing pipeline

## 📋 Prerequisites

- Python 3.12
- MongoDB
- Groq API Key
- Required Python packages (see requirements.txt)

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/nishantdeswal1810/interviewHub.git
cd interviewHub
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
FLASK_SECRET_KEY=your_secret_key_here
GROQ_API_KEY=your_groq_api_key_here
MONGO_URI=your_mongodb_connection_string( or reach out to me for data)
```


## 🚀 Running the Application

1. Start the Flask server:
```bash
python main.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## 📁 Project Structure

```
interview-assistant/
├── main.py                 # Main Flask application
├── src/
│   ├── chat.py            # ChatBot implementation
│   ├── qbank.py           # Question Bank logic
│   ├── generator.py       # PDF Q&A Generator
│   └── notes.py           # Notes management
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Chat interface
│   ├── qbank.html         # Question Bank page
│   └── pdfqa.html         # PDF Q&A Generator page
├── static/
│   ├── css/
│   └── js/
├── requirements.txt
└── .env
```

## 💡 Usage

### Chat Interface
1. Navigate to the home page
2. Select the type of interview you're preparing for
3. Specify the role and company (optional)
4. Start chatting with the AI assistant

### Question Bank
1. Click on "Q-Bank" in the navigation
2. Select a topic category
3. Browse through questions and answers
4. Use pagination to navigate through questions

### PDF Q&A Generator
1. Navigate to "PDF QA"
2. Upload a PDF document
3. Wait for the system to generate questions
4. Review and study the generated Q&A pairs

### Notes System
1. Click the sticky note icon in the bottom-right corner
2. Enter your username
3. Add, view, or delete notes
4. Notes persist across sessions


## 🔒 Security

- User data is stored securely in MongoDB
- Sensitive keys are managed through environment variables
- File upload restrictions and validations are in place
- Input sanitization is implemented

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [MongoDB](https://www.mongodb.com/)
- [Groq](https://groq.com/)
- [Font Awesome](https://fontawesome.com/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)

## 📧 Contact

For any queries or support, please contact:
- Email: msa23010@iiitl.ac.in
- GitHub: [@nishantdeswal1810](https://github.com/nishantdeswal1810)

## 🐛 Known Issues

Please report any bugs or issues in the [GitHub Issues](https://github.com/nishantdeswal1810/interviewHub/issues) section.

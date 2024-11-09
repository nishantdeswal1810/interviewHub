# generator.py

import os
from typing import List, Tuple
from dotenv import load_dotenv
from groq import Groq
from PyPDF2 import PdfReader
from io import BytesIO


# Load environment variables
load_dotenv()

class PDFGenerator:
    def __init__(self):
        api_key=os.getenv('GROQ_API_KEY')
        self.client = Groq(api_key=api_key)
        self.model = "llama3-8b-8192"
        # Add this new method to your PDFGenerator class

    def process_pdf_from_buffer(self, file_buffer) -> List[Tuple[str, str]]:
        """Process PDF from a file buffer instead of file path"""
        try:
            pdf_reader = PdfReader(file_buffer)
            text_content = ""
            
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
                
            # Split into chunks
            text_chunks = self.split_text(text_content)
            
            # Generate questions and answers
            all_qa_pairs = []
            for chunk in text_chunks:
                questions = self.generate_questions(chunk)
                
                # Generate answers for each question
                for question in questions:
                    answer = self.generate_answer(question, chunk)
                    all_qa_pairs.append((question, answer))
                    
            return all_qa_pairs
            
        except Exception as e:
            raise {e}
        
    def read_pdf_to_buffer(self, pdf_path: str) -> str:
        """Read PDF content into memory without saving"""
        try:
            text_content = ""
            pdf_reader = PdfReader(pdf_path)
            
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
                
            return text_content
        except Exception as e:
            raise {e}

    

    def split_text(self, text: str, chunk_size: int = 4000) -> List[str]:
        """Split text into chunks for processing"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) > chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks

    def generate_questions(self, text: str) -> List[str]:
        """Generate questions using Groq API"""
        system_prompt = {
            "role": "system",
            "content": """You are an expert at creating technical questions based on coding materials and documentation.
            Your goal is to prepare programmers for their coding tests. Create detailed technical questions that test
            both theoretical understanding and practical implementation skills."""
        }
        
        user_prompt = {
            "role": "user",
            "content": f"""Create 5 specific technical questions based on the following content. 
            Each question should end with a question mark and focus on important technical concepts. Don't write question number at the beginning
            
            Content: {text}"""
        }
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[system_prompt, user_prompt],
                model=self.model,
                temperature=0.7,
                max_tokens=1024,
                stream=False
            )
            
            # Extract questions from response
            questions_text = chat_completion.choices[0].message.content
            questions = [q.strip() for q in questions_text.split('\n') if '?' in q]
            return questions
            
        except Exception as e:
            raise {e}

    def generate_answer(self, question: str, context: str) -> str:
        """Generate answer for a question using Groq API"""
        try:
            system_prompt = {
                "role": "system",
                "content": "You are a technical expert providing clear, accurate answers to programming questions."
            }
            
            user_prompt = {
                "role": "user",
                "content": f"""Context: {context}

Question: {question}

Provide a clear, detailed answer focusing on practical implementation and best practices."""
            }
            
            chat_completion = self.client.chat.completions.create(
                messages=[system_prompt, user_prompt],
                model=self.model,
                temperature=0.5,
                max_tokens=1024,
                stream=False
            )
            
            return chat_completion.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    def process_pdf(self, pdf_path: str) -> List[Tuple[str, str]]:
        """Main function to process PDF and generate Q&A pairs"""
        try:
            # Read PDF content
            logger.info("Reading PDF content...")
            text_content = self.read_pdf_to_buffer(pdf_path)
            
            # Split into chunks
            text_chunks = self.split_text(text_content)
            
            # Generate questions and answers
            all_qa_pairs = []
            for chunk in text_chunks:
                questions = self.generate_questions(chunk)
                
                # Generate answers for each question
                for question in questions:
                    answer = self.generate_answer(question, chunk)
                    all_qa_pairs.append((question, answer))
                    
            return all_qa_pairs
            
        except Exception as e:
            raise {e}


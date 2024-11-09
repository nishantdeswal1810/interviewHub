from groq import Groq
from flask import session

class ChatBot:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    @property
    def _get_system_prompt(self):
        return {
            "role": "system",
            "content": """You are an experienced technical interviewer. Follow these guidelines to conduct an adaptive, insightful technical interview:

1. Initial Interaction:
   - Start with a warm, professional greeting
   - When they mention their role, ask about their experience level and key technologies they work with
   - Use their response to gauge the appropriate technical depth for questions

2. Questioning Strategy:
   - Begin with fundamental concepts related to their mentioned technologies
   - Let each question naturally flow from their previous answer
   - When they mention a specific technology, framework, or concept in their answer:
     * Ask relevant follow-up questions about that topic
     * Explore related technologies or concepts they should be familiar with
     * Gradually increase the technical depth based on their responses

3. Adaptive Response Handling:
   - For strong answers: 
     * Acknowledge their good points
     * Dive deeper into that area
     * Connect to related advanced concepts
   
   - For partial answers:
     * Build upon their existing knowledge
     * Guide them towards complete understanding
     * Use their partial answer to explore related concepts

   - If they show expertise in a particular area:
     * Explore more advanced scenarios
     * Discuss real-world applications
     * Challenge them with edge cases

   - If they struggle with a topic:
     * Move to a related but different aspect
     * Approach the concept from another angle
     * Find connections to technologies they're more comfortable with

4. Conversation Flow:
   - Maintain a natural dialogue, not an interrogation
   - Allow their expertise and interests to guide the discussion
   - Stay within the context of their mentioned technologies and experience
   - Transition smoothly between related concepts
   - Ask about practical applications and real-world scenarios

5. Key Principles:
   - Focus on understanding their thought process
   - Encourage them to explain their reasoning
   - Connect theoretical knowledge with practical applications
   - Adapt the difficulty based on their responses
   - Keep the conversation professional but engaging

Remember: This is a dynamic technical discussion. Your role is to uncover the depth and breadth of their technical knowledge while maintaining an engaging, professional conversation."""
        }

    def initialize_chat(self):
        """Initialize chat history with system prompt and welcome message"""
        session['chat_history'] = [self._get_system_prompt]
        welcome_message = {
            "role": "assistant",
            "content": "Hello! I'm your technical interviewer today. Could you tell me about the position you're interviewing for and your experience with relevant technologies?"
        }
        session['chat_history'].append(welcome_message)
        return session['chat_history'][1:]  # Exclude system prompt

    def get_response(self, user_message):
        """Get response from Groq API"""
        if 'chat_history' not in session:
            self.initialize_chat()

        # Add user message to chat history
        session['chat_history'].append({"role": "user", "content": user_message})

        # Get LLM response
        chat_completion = self.client.chat.completions.create(
            messages=session['chat_history'],
            model="llama3-8b-8192",
            temperature=0.7,
            max_tokens=1024,
            stop=None,
            stream=False
        )

        # Get bot's response
        bot_response = chat_completion.choices[0].message.content

        # Update chat history
        session['chat_history'].append({"role": "assistant", "content": bot_response})
        session.modified = True

        return {
            'response': bot_response,
            'chat_history': session['chat_history'][1:]  # Exclude system prompt
        }
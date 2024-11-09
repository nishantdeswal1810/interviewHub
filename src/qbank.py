from pymongo import MongoClient
import math

class QuestionBank:
    def __init__(self, mongo_uri):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.capstone
        self.QUESTIONS_PER_PAGE = 10

    def get_topics(self):
        """Get all available topics except 'users' collection"""
        return [name for name in self.db.list_collection_names() if name != 'users']

    def get_questions(self, topic, page=1):
        """Get paginated questions for a specific topic"""
        collection = self.db[topic]
        
        # Calculate skip and limit for pagination
        skip = (page - 1) * self.QUESTIONS_PER_PAGE
        
        # Get total questions count
        total_questions = collection.count_documents({})
        total_pages = math.ceil(total_questions / self.QUESTIONS_PER_PAGE)
        
        # Get questions for current page
        questions = list(collection.find({}).skip(skip).limit(self.QUESTIONS_PER_PAGE))
        
        # Convert ObjectId to string for JSON serialization
        for q in questions:
            q['_id'] = str(q['_id'])
        
        return {
            'questions': questions,
            'currentPage': page,
            'totalPages': total_pages,
            'totalQuestions': total_questions
        }
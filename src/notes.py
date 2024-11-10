from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

class NotesManager:
    def __init__(self, mongo_uri):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.capstone  # Using capstone database
        self.users = self.db.users
        self.notes = self.db.user_notes

    def login_user(self, username, password):
        """
        Login user or create if doesn't exist.
        Returns True if login/creation successful, False if password incorrect for existing user.
        """
        # Find user or create if doesn't exist
        user = self.users.find_one({'username': username})
        if not user:
            # Create new user
            user = {
                'username': username,
                'password': password,
                'created_at': datetime.utcnow()
            }
            self.users.insert_one(user)
            return True
        
        # If user exists, check password
        return user['password'] == password

    def save_note(self, username, note_content):
        """
        Save a new note for the user.
        Returns the MongoDB result object.
        """
        note = {
            'username': username,
            'content': note_content,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        return self.notes.insert_one(note)

    def get_notes(self, username):
        """
        Get all notes for a user, sorted by creation date (newest first).
        Returns a list of note objects with string IDs.
        """
        cursor = self.notes.find({'username': username}).sort('created_at', -1)
        notes = []
        for note in cursor:
            # Convert ObjectId to string for JSON serialization
            note['_id'] = str(note['_id'])
            notes.append(note)
        return notes

    def delete_note(self, note_id, username):
        """
        Delete a specific note for a user.
        Returns MongoDB delete result or None if ID conversion fails.
        """
        try:
            object_id = ObjectId(note_id)
            return self.notes.delete_one({
                '_id': object_id,
                'username': username  # Ensure user owns the note
            })
        except:
            return None
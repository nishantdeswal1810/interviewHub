from pymongo import MongoClient
from datetime import datetime

class NotesManager:
    def __init__(self, mongo_uri):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.interview_assistant
        self.notes = self.db.user_notes

    def save_note(self, username, note_content):
        note = {
            'username': username,
            'content': note_content,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        return self.notes.insert_one(note)

    def get_notes(self, username):
        return list(self.notes.find(
            {'username': username},
            {'_id': 0}
        ).sort('created_at', -1))

    def update_note(self, note_id, content):
        return self.notes.update_one(
            {'_id': note_id},
            {
                '$set': {
                    'content': content,
                    'updated_at': datetime.utcnow()
                }
            }
        )

    def delete_note(self, note_id):
        return self.notes.delete_one({'_id': note_id})
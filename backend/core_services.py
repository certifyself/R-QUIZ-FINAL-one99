"""
Core SocraQuest Quiz Services - POC Implementation
Handles: pack generation, answer randomization, scoring, leaderboards, quiz locking
"""
import os
import random
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client['socraquest']

# Collections
topics_col = db['topics']
questions_col = db['questions']
daily_packs_col = db['daily_packs']
attempts_col = db['attempts']
results_col = db['results']
users_col = db['users']
groups_col = db['groups']
ads_config_col = db['ads_config']  # Ad configuration collection
manual_ads_col = db['manual_ads']  # Manual ads collection
notification_settings_col = db['notification_settings']  # User notification preferences
notification_logs_col = db['notification_logs']  # Notification history
user_devices_col = db['user_devices']  # FCM tokens


def serialize_doc(doc: Optional[Dict]) -> Optional[Dict]:
    """Convert MongoDB document to JSON-serializable format"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, date):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = serialize_doc(value)
            elif isinstance(value, list):
                result[key] = serialize_doc(value)
            else:
                result[key] = value
        return result
    # Handle ObjectId at the top level (when called on list items)
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, datetime):
        return doc.isoformat()
    if isinstance(doc, date):
        return doc.isoformat()
    return doc


def generate_daily_pack(pack_date: date) -> Dict[str, Any]:
    """
    Generate daily pack with 11 quizzes.
    Each quiz contains 10 topics (30 questions total per quiz).
    
    Returns:
        {
            'date': str (YYYY-MM-DD),
            'quizzes': [
                {
                    'index': 0-10,
                    'topic_ids': [ObjectId x 10]  # 10 topics per quiz
                }
            ],
            'generated_at': datetime
        }
    """
    # Convert date to string for MongoDB storage
    date_str = pack_date.isoformat() if isinstance(pack_date, date) else pack_date
    
    # Check if pack already exists
    existing = daily_packs_col.find_one({'date': date_str})
    if existing:
        return serialize_doc(existing)
    
    # Get all active topics with at least 3 questions
    active_topics = []
    for topic in topics_col.find({'active': True}):
        q_count = questions_col.count_documents({
            'topic_id': topic['_id'],
            'active': True
        })
        if q_count >= 3:
            active_topics.append(topic['_id'])
    
    # Need at least 110 topics (11 quizzes × 10 topics each)
    # But can reuse topics across different quizzes
    if len(active_topics) < 10:
        raise ValueError(f"Need at least 10 topics with 3+ questions each. Found: {len(active_topics)}")
    
    # Use date as seed for deterministic selection
    seed = int(pack_date.strftime('%Y%m%d'))
    rng = random.Random(seed)
    
    # Generate 11 quizzes, each with 10 topics
    quizzes = []
    for quiz_idx in range(11):
        # Shuffle topics for this quiz
        shuffled = active_topics.copy()
        rng.shuffle(shuffled)
        
        # Select 10 topics for this quiz
        quiz_topics = shuffled[:10]
        
        quizzes.append({
            'index': quiz_idx,
            'topic_ids': quiz_topics
        })
    
    # Create pack document
    pack = {
        'date': date_str,
        'quizzes': quizzes,
        'generated_at': datetime.utcnow()
    }
    
    result = daily_packs_col.insert_one(pack)
    pack['_id'] = result.inserted_id
    
    return serialize_doc(pack)


def get_quiz_questions(topic_id: str, attempt_num: int = 1, language: str = 'en') -> List[Dict[str, Any]]:
    """
    Get 3 questions for a topic with randomized answer options.
    Different randomization for each attempt.
    Returns questions in specified language.
    
    Args:
        topic_id: Topic ID
        attempt_num: Attempt number (for randomization seed)
        language: 'en' or 'sk'
    
    Returns:
        [
            {
                '_id': str,
                'text': str (in specified language),
                'options': [{'key': 'A', 'label': str (in specified language)}, ...],
                'correct_key': str (only for answer reveal)
            }
        ]
    """
    topic_oid = ObjectId(topic_id)
    
    # Get 3 random active questions for this topic
    questions = list(questions_col.find({
        'topic_id': topic_oid,
        'active': True
    }).limit(3))
    
    if len(questions) < 3:
        raise ValueError(f"Topic {topic_id} has fewer than 3 active questions")
    
    # Randomize answer order for each question based on attempt number
    result = []
    for q in questions:
        # Use question ID + attempt number as seed
        seed = str(q['_id']) + str(attempt_num)
        rng = random.Random(seed)
        
        # Get text in specified language
        text = q['text']
        if isinstance(text, dict):
            text = text.get(language, text.get('en', ''))
        
        # Get options and translate
        options = []
        for opt in q['options']:
            label = opt['label']
            if isinstance(label, dict):
                label = label.get(language, label.get('en', ''))
            options.append({
                'key': opt['key'],
                'label': label
            })
        
        # Shuffle options
        rng.shuffle(options)
        
        result.append({
            '_id': str(q['_id']),
            'text': text,
            'options': options,
            'correct_key': q['correct_key'],
            'image_url': q.get('image_url', None)  # Include image URL if present
        })
    
    return result


def score_attempt(answers: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Score user answers against correct answers.
    
    Args:
        answers: [{'question_id': str, 'choice_key': str}, ...]
                 choice_key can be 'UNANSWERED' if time expired
    
    Returns:
        {
            'correct_count': int,
            'total': int,
            'percentage': float,
            'details': [{'question_id': str, 'correct': bool}, ...]
        }
    """
    details = []
    correct_count = 0
    
    for ans in answers:
        q_id = ObjectId(ans['question_id'])
        question = questions_col.find_one({'_id': q_id})
        
        if not question:
            continue
        
        # Check if answered and correct
        is_correct = (ans['choice_key'] != 'UNANSWERED' and 
                     ans['choice_key'] == question['correct_key'])
        if is_correct:
            correct_count += 1
        
        details.append({
            'question_id': ans['question_id'],
            'correct': is_correct
        })
    
    total = len(answers)
    percentage = (correct_count / total * 100) if total > 0 else 0
    
    return {
        'correct_count': correct_count,
        'total': total,
        'percentage': percentage,
        'details': details
    }


def record_attempt(user_id: str, pack_date: date, quiz_index: int, 
                   attempt_num: int, answers: List[Dict], time_ms: int) -> Dict[str, Any]:
    """
    Record quiz attempt and update best result if needed.
    
    Returns:
        {
            'attempt_id': str,
            'score': {...},
            'is_best': bool
        }
    """
    # Convert date to string for MongoDB storage
    date_str = pack_date.isoformat() if isinstance(pack_date, date) else pack_date
    
    # Score the attempt
    score = score_attempt(answers)
    
    # Save attempt record
    attempt_doc = {
        'user_id': ObjectId(user_id),
        'date': date_str,
        'quiz_index': quiz_index,
        'attempt_num': attempt_num,
        'answers': answers,
        'correct_count': score['correct_count'],
        'time_ms': time_ms,
        'percentage': score['percentage'],
        'finished_at': datetime.utcnow()
    }
    
    result = attempts_col.insert_one(attempt_doc)
    attempt_id = str(result.inserted_id)
    
    # Update best result
    is_best = upsert_best_result(user_id, date_str, quiz_index, 
                                   score['percentage'], time_ms)
    
    return {
        'attempt_id': attempt_id,
        'score': score,
        'is_best': is_best
    }


def upsert_best_result(user_id: str, pack_date, quiz_index: int,
                       percentage: float, time_ms: int) -> bool:
    """
    Update best result for user/date/quiz if current is better.
    Better = higher percentage, or same percentage but faster time.
    
    Args:
        pack_date: date object or string (YYYY-MM-DD)
    
    Returns:
        True if this is the new best result
    """
    # Convert date to string if needed
    date_str = pack_date.isoformat() if isinstance(pack_date, date) else pack_date
    user_oid = ObjectId(user_id)
    
    existing = results_col.find_one({
        'user_id': user_oid,
        'date': date_str,
        'quiz_index': quiz_index
    })
    
    is_best = False
    
    if not existing:
        # First attempt - always best
        results_col.insert_one({
            'user_id': user_oid,
            'date': date_str,
            'quiz_index': quiz_index,
            'best_pct': percentage,
            'best_time_ms': time_ms,
            'locked_after_answers': False,
            'updated_at': datetime.utcnow()
        })
        is_best = True
    else:
        # Check if current is better
        if (percentage > existing['best_pct'] or 
            (percentage == existing['best_pct'] and time_ms < existing['best_time_ms'])):
            results_col.update_one(
                {'_id': existing['_id']},
                {
                    '$set': {
                        'best_pct': percentage,
                        'best_time_ms': time_ms,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            is_best = True
    
    return is_best


def compute_leaderboard(pack_date, quiz_index: int, 
                        group_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Compute leaderboard for a quiz.
    Sort by: percentage DESC, then time_ms ASC
    
    Args:
        pack_date: date object or string (YYYY-MM-DD)
        quiz_index: Quiz index (0-9 for regular, 10 for bonus)
        group_id: Optional group filter
    
    Returns:
        [
            {
                'rank': int,
                'user_id': str,
                'nickname': str,
                'percentage': float,
                'time_ms': int
            }
        ]
    """
    # Convert date to string if needed
    date_str = pack_date.isoformat() if isinstance(pack_date, date) else pack_date
    
    # Build query filter
    query = {
        'date': date_str,
        'quiz_index': quiz_index
    }
    
    # Filter by group members if group_id provided
    if group_id:
        group = groups_col.find_one({'_id': ObjectId(group_id)})
        if group and 'members' in group:
            query['user_id'] = {'$in': group['members']}
    
    # Get results sorted by percentage DESC, time ASC
    results = list(results_col.find(query).sort([
        ('best_pct', DESCENDING),
        ('best_time_ms', ASCENDING)
    ]))
    
    # Build leaderboard with user info
    leaderboard = []
    for idx, result in enumerate(results):
        user = users_col.find_one({'_id': result['user_id']})
        
        leaderboard.append({
            'rank': idx + 1,
            'user_id': str(result['user_id']),
            'nickname': user['nickname'] if user else 'Unknown',
            'percentage': result['best_pct'],
            'time_ms': result['best_time_ms']
        })
    
    return leaderboard


def lock_quiz_after_answers(user_id: str, pack_date, quiz_index: int) -> bool:
    """
    Lock quiz for user after they view correct answers.
    User cannot attempt quiz again after this.
    
    Args:
        pack_date: date object or string (YYYY-MM-DD)
    
    Returns:
        True if successfully locked
    """
    # Convert date to string if needed
    date_str = pack_date.isoformat() if isinstance(pack_date, date) else pack_date
    user_oid = ObjectId(user_id)
    
    result = results_col.update_one(
        {
            'user_id': user_oid,
            'date': date_str,
            'quiz_index': quiz_index
        },
        {
            '$set': {
                'locked_after_answers': True,
                'locked_at': datetime.utcnow()
            }
        },
        upsert=True
    )
    
    return result.modified_count > 0 or result.upserted_id is not None


def get_attempt_count(user_id: str, pack_date, quiz_index: int) -> int:
    """Get number of attempts user has made for a quiz"""
    # Convert date to string if needed
    date_str = pack_date.isoformat() if isinstance(pack_date, date) else pack_date
    return attempts_col.count_documents({
        'user_id': ObjectId(user_id),
        'date': date_str,
        'quiz_index': quiz_index
    })


def is_quiz_locked(user_id: str, pack_date, quiz_index: int) -> bool:
    """Check if quiz is locked for user"""
    # Convert date to string if needed
    date_str = pack_date.isoformat() if isinstance(pack_date, date) else pack_date
    result = results_col.find_one({
        'user_id': ObjectId(user_id),
        'date': date_str,
        'quiz_index': quiz_index,
        'locked_after_answers': True
    })
    return result is not None


def create_indexes():
    """Create necessary database indexes for performance"""
    # Results: leaderboard queries
    results_col.create_index([
        ('date', ASCENDING),
        ('quiz_index', ASCENDING),
        ('best_pct', DESCENDING),
        ('best_time_ms', ASCENDING)
    ])
    
    # Results: user lookup
    results_col.create_index([
        ('user_id', ASCENDING),
        ('date', ASCENDING),
        ('quiz_index', ASCENDING)
    ])
    
    # Attempts: user history
    attempts_col.create_index([
        ('user_id', ASCENDING),
        ('date', ASCENDING),
        ('quiz_index', ASCENDING),
        ('attempt_num', ASCENDING)
    ])
    
    # Daily packs: date lookup
    daily_packs_col.create_index([('date', ASCENDING)], unique=True)
    
    # Topics
    topics_col.create_index([('active', ASCENDING)])
    
    # Questions
    questions_col.create_index([
        ('topic_id', ASCENDING),
        ('active', ASCENDING)
    ])
    
    print("✅ Indexes created successfully")


if __name__ == '__main__':
    # Create indexes when module is run directly
    create_indexes()

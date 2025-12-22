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
used_questions_col = db['used_questions']  # Track globally used questions to prevent repeats


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
    
    QUESTION NON-REPEAT LOGIC:
    - Tracks all questions used globally in 'used_questions' collection
    - Questions won't repeat until ALL questions in the database have been used
    - Once all questions are exhausted, the tracking resets automatically
    
    Returns:
        {
            'date': str (YYYY-MM-DD),
            'quizzes': [
                {
                    'index': 0-10,
                    'topic_ids': [ObjectId x 10],
                    'question_ids': [[q1, q2, q3] x 10]  # Pre-selected questions
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
    
    if len(active_topics) < 10:
        raise ValueError(f"Need at least 10 topics with 3+ questions each. Found: {len(active_topics)}")
    
    # Get set of already-used question IDs
    used_question_ids = set()
    used_doc = used_questions_col.find_one({'_id': 'global_tracker'})
    if used_doc and 'question_ids' in used_doc:
        used_question_ids = set(used_doc['question_ids'])
    
    # Get total active questions count
    total_active_questions = questions_col.count_documents({'active': True})
    
    # Check if we need to reset (all questions used)
    # We need 330 questions per day (11 quizzes × 10 topics × 3 questions)
    questions_needed_today = 330
    available_unused = total_active_questions - len(used_question_ids)
    
    if available_unused < questions_needed_today:
        # Reset tracking - all questions have been used
        print(f"🔄 Resetting question tracker. Used: {len(used_question_ids)}, Total: {total_active_questions}")
        used_question_ids = set()
        used_questions_col.update_one(
            {'_id': 'global_tracker'},
            {'$set': {'question_ids': [], 'last_reset': datetime.utcnow()}},
            upsert=True
        )
    
    # Use date as seed for deterministic topic selection
    seed = int(pack_date.strftime('%Y%m%d'))
    rng = random.Random(seed)
    
    # Shuffle all topics once for the day
    shuffled_topics = active_topics.copy()
    rng.shuffle(shuffled_topics)
    
    # Find Image Quiz topic (for Quiz 5, Topic 1)
    image_quiz_topic = topics_col.find_one({'name': 'Image Quiz', 'active': True})
    image_quiz_topic_id = image_quiz_topic['_id'] if image_quiz_topic else None
    
    # Generate 11 quizzes, minimizing topic repeats
    quizzes = []
    used_topic_count = {}
    newly_used_question_ids = []  # Track questions used in this pack
    
    for quiz_idx in range(11):
        quiz_topics = []
        quiz_question_ids = []  # Store pre-selected question IDs for each topic
        
        # Try to select 10 topics, preferring those used least
        candidates = shuffled_topics.copy()
        
        for topic_slot in range(10):
            # SPECIAL CASE: Quiz 5 (index 4), Topic 1 (slot 0) = Image Quiz
            if quiz_idx == 4 and topic_slot == 0 and image_quiz_topic_id:
                # Force Image Quiz topic for Quiz 5, first topic
                topic_questions = select_questions_for_topic(
                    image_quiz_topic_id, 
                    used_question_ids, 
                    rng
                )
                
                if len(topic_questions) >= 3:
                    quiz_topics.append(image_quiz_topic_id)
                    selected_q_ids = [str(q['_id']) for q in topic_questions[:3]]
                    quiz_question_ids.append(selected_q_ids)
                    
                    for q_id in selected_q_ids:
                        used_question_ids.add(q_id)
                        newly_used_question_ids.append(q_id)
                    
                    used_topic_count[str(image_quiz_topic_id)] = used_topic_count.get(str(image_quiz_topic_id), 0) + 1
                    if image_quiz_topic_id in candidates:
                        candidates.remove(image_quiz_topic_id)
                    continue
            
            if not candidates:
                # Ran out of candidates, reshuffle and continue
                candidates = shuffled_topics.copy()
                rng.shuffle(candidates)
            
            # Find topic used least frequently
            best_topic = None
            min_usage = float('inf')
            
            for topic in candidates:
                topic_str = str(topic)
                usage = used_topic_count.get(topic_str, 0)
                if usage < min_usage:
                    min_usage = usage
                    best_topic = topic
            
            if best_topic:
                # Select 3 questions for this topic, excluding already-used ones
                topic_questions = select_questions_for_topic(
                    best_topic, 
                    used_question_ids, 
                    rng
                )
                
                if len(topic_questions) >= 3:
                    quiz_topics.append(best_topic)
                    selected_q_ids = [str(q['_id']) for q in topic_questions[:3]]
                    quiz_question_ids.append(selected_q_ids)
                    
                    # Mark these questions as used
                    for q_id in selected_q_ids:
                        used_question_ids.add(q_id)
                        newly_used_question_ids.append(q_id)
                    
                    used_topic_count[str(best_topic)] = used_topic_count.get(str(best_topic), 0) + 1
                    candidates.remove(best_topic)
                else:
                    # Topic doesn't have enough unused questions, skip it
                    candidates.remove(best_topic)
        
        quizzes.append({
            'index': quiz_idx,
            'topic_ids': quiz_topics,
            'question_ids': quiz_question_ids  # Pre-selected questions
        })
    
    # Update the global used questions tracker
    if newly_used_question_ids:
        used_questions_col.update_one(
            {'_id': 'global_tracker'},
            {
                '$addToSet': {'question_ids': {'$each': newly_used_question_ids}},
                '$set': {'last_updated': datetime.utcnow()}
            },
            upsert=True
        )
    
    # Create pack document
    pack = {
        'date': date_str,
        'quizzes': quizzes,
        'generated_at': datetime.utcnow(),
        'questions_used': len(newly_used_question_ids),
        'total_used_after': len(used_question_ids)
    }
    
    result = daily_packs_col.insert_one(pack)
    pack['_id'] = result.inserted_id
    
    print(f"✅ Generated pack for {date_str}: {len(newly_used_question_ids)} new questions used, {len(used_question_ids)}/{total_active_questions} total used")
    
    return serialize_doc(pack)


def select_questions_for_topic(topic_id, used_question_ids: set, rng: random.Random) -> List[Dict]:
    """
    Select questions for a topic, prioritizing unused questions.
    
    Args:
        topic_id: The topic ObjectId
        used_question_ids: Set of already-used question ID strings
        rng: Random number generator for shuffling
    
    Returns:
        List of question documents (up to 3)
    """
    topic_oid = ObjectId(topic_id) if not isinstance(topic_id, ObjectId) else topic_id
    
    # Get all active questions for this topic
    all_questions = list(questions_col.find({
        'topic_id': topic_oid,
        'active': True
    }))
    
    # Separate into unused and used
    unused_questions = [q for q in all_questions if str(q['_id']) not in used_question_ids]
    used_questions = [q for q in all_questions if str(q['_id']) in used_question_ids]
    
    # Shuffle both lists
    rng.shuffle(unused_questions)
    rng.shuffle(used_questions)
    
    # Prioritize unused questions
    selected = []
    
    # First, take from unused
    for q in unused_questions:
        if len(selected) >= 3:
            break
        selected.append(q)
    
    # If we still need more, take from used (fallback)
    if len(selected) < 3:
        for q in used_questions:
            if len(selected) >= 3:
                break
            selected.append(q)
    
    return selected


def get_quiz_questions(topic_ids: List, attempt_num: int = 1, language: str = 'en', 
                       pack_date: date = None, quiz_index: int = None) -> List[Dict[str, Any]]:
    """
    Get questions for multiple topics with randomized answer options.
    Different randomization for each attempt.
    Returns questions in specified language.
    
    Uses PRE-SELECTED questions from the daily pack to ensure no question repeats
    until all 1000 questions have been used.
    
    Args:
        topic_ids: List of topic IDs (10 topics)
        attempt_num: Attempt number (for randomization seed)
        language: 'en' or 'sk'
        pack_date: Date of the pack (to retrieve pre-selected questions)
        quiz_index: Index of the quiz in the pack
    
    Returns:
        List of 30 questions (10 topics × 3 questions each)
        [
            {
                '_id': str,
                'text': str (in specified language),
                'topic_name': str,
                'topic_index': int (0-9),
                'options': [{'key': 'A', 'label': str}, ...],
                'correct_key': str
            }
        ]
    """
    all_questions = []
    
    # Try to get pre-selected questions from pack
    pre_selected_questions = None
    if pack_date and quiz_index is not None:
        date_str = pack_date.isoformat() if isinstance(pack_date, date) else pack_date
        pack = daily_packs_col.find_one({'date': date_str})
        if pack and 'quizzes' in pack:
            for quiz in pack['quizzes']:
                if quiz['index'] == quiz_index and 'question_ids' in quiz:
                    pre_selected_questions = quiz['question_ids']
                    break
    
    for topic_idx, topic_id in enumerate(topic_ids):
        topic_oid = ObjectId(topic_id)
        
        # Get topic info
        topic = topics_col.find_one({'_id': topic_oid})
        topic_name = topic['name'] if topic else 'Unknown'
        
        # Use pre-selected questions if available
        if pre_selected_questions and topic_idx < len(pre_selected_questions):
            question_ids = pre_selected_questions[topic_idx]
            questions = []
            for q_id in question_ids:
                q = questions_col.find_one({'_id': ObjectId(q_id), 'active': True})
                if q:
                    questions.append(q)
            
            # If some pre-selected questions are missing, fall back to random selection
            if len(questions) < 3:
                additional = list(questions_col.aggregate([
                    {'$match': {'topic_id': topic_oid, 'active': True, '_id': {'$nin': [ObjectId(qid) for qid in question_ids]}}},
                    {'$sample': {'size': 3 - len(questions)}}
                ]))
                questions.extend(additional)
        else:
            # Fallback: Get 3 random active questions for this topic
            questions = list(questions_col.aggregate([
                {'$match': {'topic_id': topic_oid, 'active': True}},
                {'$sample': {'size': 3}}
            ]))
        
        if len(questions) < 3:
            raise ValueError(f"Topic {topic_id} ({topic_name}) has fewer than 3 active questions")
        
        # Process each question
        for q in questions[:3]:
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
            
            # Sort options by key to ensure A, B, C, D order
            options.sort(key=lambda x: x['key'])
            
            all_questions.append({
                '_id': str(q['_id']),
                'text': text,
                'topic_name': topic_name,
                'topic_index': topic_idx,
                'options': options,
                'correct_key': q['correct_key'],
                'image_url': q.get('image_url', None)
            })
    
    return all_questions


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


def get_question_usage_stats() -> Dict[str, Any]:
    """
    Get statistics about question usage for the no-repeat system.
    
    Returns:
        {
            'total_questions': int,
            'used_questions': int,
            'remaining_questions': int,
            'usage_percentage': float,
            'last_reset': datetime or None,
            'last_updated': datetime or None
        }
    """
    total_active = questions_col.count_documents({'active': True})
    
    tracker = used_questions_col.find_one({'_id': 'global_tracker'})
    
    if tracker:
        used_count = len(tracker.get('question_ids', []))
        return {
            'total_questions': total_active,
            'used_questions': used_count,
            'remaining_questions': total_active - used_count,
            'usage_percentage': round((used_count / total_active * 100), 2) if total_active > 0 else 0,
            'last_reset': tracker.get('last_reset'),
            'last_updated': tracker.get('last_updated')
        }
    
    return {
        'total_questions': total_active,
        'used_questions': 0,
        'remaining_questions': total_active,
        'usage_percentage': 0,
        'last_reset': None,
        'last_updated': None
    }


def reset_question_usage() -> Dict[str, Any]:
    """
    Manually reset the question usage tracker.
    This will allow all questions to be used again.
    
    Returns:
        {'success': True, 'message': str}
    """
    result = used_questions_col.update_one(
        {'_id': 'global_tracker'},
        {
            '$set': {
                'question_ids': [],
                'last_reset': datetime.utcnow(),
                'reset_reason': 'manual'
            }
        },
        upsert=True
    )
    
    return {
        'success': True,
        'message': 'Question usage tracker has been reset. All questions are now available.'
    }


if __name__ == '__main__':
    # Create indexes when module is run directly
    create_indexes()

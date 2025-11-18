from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from bson import ObjectId
import os
import jwt
import bcrypt
from pymongo import MongoClient, ASCENDING, DESCENDING

# Import core services
from core_services import (
    generate_daily_pack,
    get_quiz_questions,
    score_attempt,
    record_attempt,
    compute_leaderboard,
    lock_quiz_after_answers,
    get_attempt_count,
    is_quiz_locked,
    serialize_doc,
    db,
    users_col,
    topics_col,
    questions_col,
    daily_packs_col,
    attempts_col,
    results_col,
    groups_col
)

app = FastAPI(title="SocraQuest API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET', 'socraquest-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'

# ============================================================================
# MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    nickname: str = Field(min_length=2, max_length=50)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict

class TopicCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    active: bool = True

class TopicUpdate(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None

class QuestionOption(BaseModel):
    key: str  # A, B, C, D
    label: str

class QuestionCreate(BaseModel):
    topic_id: str
    text: str = Field(min_length=5)
    options: List[QuestionOption] = Field(min_length=4, max_length=4)
    correct_key: str  # A, B, C, or D
    active: bool = True

class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    options: Optional[List[QuestionOption]] = None
    correct_key: Optional[str] = None
    active: Optional[bool] = None

class AnswerSubmit(BaseModel):
    question_id: str
    choice_key: str

class QuizSubmit(BaseModel):
    answers: List[AnswerSubmit]
    time_ms: int

class GroupCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)

class GroupJoin(BaseModel):
    code: str = Field(min_length=6, max_length=10)

# ============================================================================
# AUTH HELPERS
# ============================================================================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, email: str, role: str) -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> Dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    payload = decode_token(credentials.credentials)
    user = users_col.find_one({'_id': ObjectId(payload['user_id'])})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return serialize_doc(user)

def get_current_admin(current_user: Dict = Depends(get_current_user)) -> Dict:
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.post("/api/auth/register", response_model=TokenResponse)
def register(data: RegisterRequest):
    # Check if user exists
    if users_col.find_one({'email': data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_doc = {
        'email': data.email,
        'password_hash': hash_password(data.password),
        'nickname': data.nickname,
        'role': 'user',
        'avatar_seed': data.nickname[0].upper(),
        'stats': {
            'quizzes_played': 0,
            'avg_correct': 0,
            'personal_best': 0
        },
        'badges': [],
        'created_at': datetime.utcnow()
    }
    
    result = users_col.insert_one(user_doc)
    user_doc['_id'] = result.inserted_id
    
    # Create token
    token = create_token(str(result.inserted_id), data.email, 'user')
    
    user_data = serialize_doc(user_doc)
    user_data.pop('password_hash', None)
    
    return {
        'access_token': token,
        'token_type': 'bearer',
        'user': user_data
    }

@app.post("/api/auth/login", response_model=TokenResponse)
def login(data: LoginRequest):
    user = users_col.find_one({'email': data.email})
    
    if not user or not verify_password(data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(str(user['_id']), user['email'], user.get('role', 'user'))
    
    user_data = serialize_doc(user)
    user_data.pop('password_hash', None)
    
    return {
        'access_token': token,
        'token_type': 'bearer',
        'user': user_data
    }

@app.get("/api/auth/me")
def get_me(current_user: Dict = Depends(get_current_user)):
    current_user.pop('password_hash', None)
    return current_user

# ============================================================================
# ADMIN - TOPICS
# ============================================================================

@app.get("/api/admin/topics")
def get_topics_admin(current_user: Dict = Depends(get_current_admin)):
    topics = list(topics_col.find())
    
    # Add question count to each topic
    for topic in topics:
        topic['question_count'] = questions_col.count_documents({
            'topic_id': topic['_id'],
            'active': True
        })
    
    return {'topics': serialize_doc(topics)}

@app.post("/api/admin/topics")
def create_topic_admin(data: TopicCreate, current_user: Dict = Depends(get_current_admin)):
    topic_doc = {
        'name': data.name,
        'active': data.active,
        'created_at': datetime.utcnow()
    }
    
    result = topics_col.insert_one(topic_doc)
    topic_doc['_id'] = result.inserted_id
    
    return {'topic': serialize_doc(topic_doc)}

@app.put("/api/admin/topics/{topic_id}")
def update_topic_admin(topic_id: str, data: TopicUpdate, current_user: Dict = Depends(get_current_admin)):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data['updated_at'] = datetime.utcnow()
    
    result = topics_col.update_one(
        {'_id': ObjectId(topic_id)},
        {'$set': update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    topic = topics_col.find_one({'_id': ObjectId(topic_id)})
    return {'topic': serialize_doc(topic)}

@app.delete("/api/admin/topics/{topic_id}")
def delete_topic_admin(topic_id: str, current_user: Dict = Depends(get_current_admin)):
    # Check if topic has questions
    q_count = questions_col.count_documents({'topic_id': ObjectId(topic_id)})
    if q_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete topic with {q_count} questions. Delete questions first."
        )
    
    result = topics_col.delete_one({'_id': ObjectId(topic_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return {'success': True}

# ============================================================================
# ADMIN - QUESTIONS
# ============================================================================

@app.get("/api/admin/questions")
def get_questions_admin(
    topic_id: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_admin)
):
    query = {}
    if topic_id:
        query['topic_id'] = ObjectId(topic_id)
    
    questions = list(questions_col.find(query))
    
    # Add topic name to each question
    for q in questions:
        topic = topics_col.find_one({'_id': q['topic_id']})
        q['topic_name'] = topic['name'] if topic else 'Unknown'
    
    return {'questions': serialize_doc(questions)}

@app.post("/api/admin/questions")
def create_question_admin(data: QuestionCreate, current_user: Dict = Depends(get_current_admin)):
    # Validate topic exists
    topic = topics_col.find_one({'_id': ObjectId(data.topic_id)})
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Validate correct_key
    if data.correct_key not in ['A', 'B', 'C', 'D']:
        raise HTTPException(status_code=400, detail="correct_key must be A, B, C, or D")
    
    # Validate options
    option_keys = [opt.key for opt in data.options]
    if set(option_keys) != {'A', 'B', 'C', 'D'}:
        raise HTTPException(status_code=400, detail="Options must include exactly A, B, C, D")
    
    question_doc = {
        'topic_id': ObjectId(data.topic_id),
        'text': data.text,
        'options': [opt.dict() for opt in data.options],
        'correct_key': data.correct_key,
        'active': data.active,
        'created_at': datetime.utcnow()
    }
    
    result = questions_col.insert_one(question_doc)
    question_doc['_id'] = result.inserted_id
    question_doc['topic_name'] = topic['name']
    
    return {'question': serialize_doc(question_doc)}

@app.put("/api/admin/questions/{question_id}")
def update_question_admin(
    question_id: str, 
    data: QuestionUpdate, 
    current_user: Dict = Depends(get_current_admin)
):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Validate correct_key if provided
    if 'correct_key' in update_data and update_data['correct_key'] not in ['A', 'B', 'C', 'D']:
        raise HTTPException(status_code=400, detail="correct_key must be A, B, C, or D")
    
    # Validate options if provided
    if 'options' in update_data:
        option_keys = [opt['key'] for opt in update_data['options']]
        if set(option_keys) != {'A', 'B', 'C', 'D'}:
            raise HTTPException(status_code=400, detail="Options must include exactly A, B, C, D")
    
    update_data['updated_at'] = datetime.utcnow()
    
    result = questions_col.update_one(
        {'_id': ObjectId(question_id)},
        {'$set': update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question = questions_col.find_one({'_id': ObjectId(question_id)})
    return {'question': serialize_doc(question)}

@app.delete("/api/admin/questions/{question_id}")
def delete_question_admin(question_id: str, current_user: Dict = Depends(get_current_admin)):
    result = questions_col.delete_one({'_id': ObjectId(question_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return {'success': True}

# ============================================================================
# ADMIN - DAILY PACKS
# ============================================================================

@app.get("/api/admin/packs")
def get_packs_admin(
    date_str: Optional[str] = Query(None, alias="date"),
    current_user: Dict = Depends(get_current_admin)
):
    query = {}
    if date_str:
        query['date'] = date_str
    
    packs = list(daily_packs_col.find(query).sort('date', DESCENDING).limit(30))
    
    # Add topic names
    for pack in packs:
        pack['quiz_topics'] = []
        for topic_id in pack.get('quiz_topic_ids', []):
            topic = topics_col.find_one({'_id': topic_id})
            pack['quiz_topics'].append({
                '_id': str(topic_id),
                'name': topic['name'] if topic else 'Unknown'
            })
        
        bonus_topic = topics_col.find_one({'_id': pack.get('bonus_topic_id')})
        pack['bonus_topic'] = {
            '_id': str(pack.get('bonus_topic_id')),
            'name': bonus_topic['name'] if bonus_topic else 'Unknown'
        }
    
    return {'packs': serialize_doc(packs)}

@app.post("/api/admin/packs/generate")
def generate_pack_admin(
    date_str: str = Query(..., alias="date"),
    current_user: Dict = Depends(get_current_admin)
):
    try:
        pack_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    try:
        pack = generate_daily_pack(pack_date)
        return {'pack': pack}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/admin/packs/{date_str}/questions")
def get_pack_questions_admin(
    date_str: str,
    current_user: Dict = Depends(get_current_admin)
):
    pack = daily_packs_col.find_one({'date': date_str})
    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")
    
    quizzes = []
    for idx, topic_id in enumerate(pack['quiz_topic_ids']):
        topic = topics_col.find_one({'_id': topic_id})
        questions = list(questions_col.find({
            'topic_id': topic_id,
            'active': True
        }).limit(3))
        
        quizzes.append({
            'index': idx,
            'topic': serialize_doc(topic),
            'questions': serialize_doc(questions),
            'question_count': len(questions)
        })
    
    # Bonus quiz
    bonus_topic = topics_col.find_one({'_id': pack['bonus_topic_id']})
    bonus_questions = list(questions_col.find({
        'topic_id': pack['bonus_topic_id'],
        'active': True
    }).limit(3))
    
    bonus_quiz = {
        'index': 10,
        'topic': serialize_doc(bonus_topic),
        'questions': serialize_doc(bonus_questions),
        'question_count': len(bonus_questions)
    }
    
    return {
        'quizzes': quizzes,
        'bonus_quiz': bonus_quiz,
        'total_questions': sum(q['question_count'] for q in quizzes) * 10 + bonus_quiz['question_count']
    }

@app.get("/api/admin/metrics")
def get_metrics_admin(current_user: Dict = Depends(get_current_admin)):
    today = date.today().isoformat()
    
    total_users = users_col.count_documents({'role': 'user'})
    
    quizzes_played_today = attempts_col.count_documents({
        'date': today
    })
    
    # Calculate average success
    today_attempts = list(attempts_col.find({'date': today}))
    avg_success = 0
    if today_attempts:
        avg_success = sum(a.get('percentage', 0) for a in today_attempts) / len(today_attempts)
    
    return {
        'total_users': total_users,
        'quizzes_played_today': quizzes_played_today,
        'avg_success_rate': round(avg_success, 1)
    }

# ============================================================================
# USER - DAILY PACKS
# ============================================================================

@app.get("/api/packs/today")
def get_today_pack(current_user: Dict = Depends(get_current_user)):
    today = date.today()
    
    try:
        pack = generate_daily_pack(today)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Get user progress for each quiz
    user_id = current_user['_id']
    today_str = today.isoformat()
    
    quizzes = []
    for idx, topic_id in enumerate(pack['quiz_topic_ids']):
        topic = topics_col.find_one({'_id': ObjectId(topic_id)})
        
        # Get attempt count and lock status
        attempt_count = get_attempt_count(user_id, today, idx)
        is_locked = is_quiz_locked(user_id, today, idx)
        
        # Get best result
        result = results_col.find_one({
            'user_id': ObjectId(user_id),
            'date': today_str,
            'quiz_index': idx
        })
        
        best_score = None
        if result:
            best_score = {
                'percentage': result.get('best_pct', 0),
                'time_ms': result.get('best_time_ms', 0)
            }
        
        quizzes.append({
            'index': idx,
            'topic': serialize_doc(topic),
            'attempt_count': attempt_count,
            'is_locked': is_locked,
            'best_score': best_score,
            'status': 'locked' if is_locked else ('completed' if attempt_count >= 3 else ('in_progress' if attempt_count > 0 else 'available'))
        })
    
    # Check if bonus unlocked (all 10 regular quizzes completed)
    all_completed = all(q['attempt_count'] > 0 for q in quizzes)
    
    bonus_topic = topics_col.find_one({'_id': ObjectId(pack['bonus_topic_id'])})
    bonus_attempt_count = get_attempt_count(user_id, today, 10)
    bonus_locked = is_quiz_locked(user_id, today, 10)
    
    bonus_result = results_col.find_one({
        'user_id': ObjectId(user_id),
        'date': today_str,
        'quiz_index': 10
    })
    
    bonus_best_score = None
    if bonus_result:
        bonus_best_score = {
            'percentage': bonus_result.get('best_pct', 0),
            'time_ms': bonus_result.get('best_time_ms', 0)
        }
    
    bonus_quiz = {
        'index': 10,
        'topic': serialize_doc(bonus_topic),
        'unlocked': all_completed,
        'attempt_count': bonus_attempt_count,
        'is_locked': bonus_locked,
        'best_score': bonus_best_score,
        'status': 'locked' if bonus_locked else ('completed' if bonus_attempt_count >= 3 else ('in_progress' if bonus_attempt_count > 0 else ('available' if all_completed else 'locked')))
    }
    
    return {
        'date': today_str,
        'quizzes': quizzes,
        'bonus_quiz': bonus_quiz
    }

# ============================================================================
# USER - QUIZ TAKING
# ============================================================================

@app.get("/api/quizzes/{quiz_index}")
def get_quiz(
    quiz_index: int,
    lang: str = Query('en', regex='^(en|sk)$'),
    current_user: Dict = Depends(get_current_user)
):
    if quiz_index < 0 or quiz_index > 10:
        raise HTTPException(status_code=400, detail="Quiz index must be 0-10")
    
    user_id = current_user['_id']
    today = date.today()
    today_str = today.isoformat()
    
    # Check if quiz is locked
    if is_quiz_locked(user_id, today, quiz_index):
        raise HTTPException(status_code=403, detail="Quiz is locked after viewing answers")
    
    # Get attempt count
    attempt_count = get_attempt_count(user_id, today, quiz_index)
    
    if attempt_count >= 3:
        raise HTTPException(status_code=403, detail="Maximum 3 attempts reached")
    
    # Get pack
    pack = generate_daily_pack(today)
    
    # Get topic ID
    if quiz_index == 10:
        # Bonus quiz - check if unlocked
        regular_attempts = [get_attempt_count(user_id, today, i) for i in range(10)]
        if not all(count > 0 for count in regular_attempts):
            raise HTTPException(status_code=403, detail="Complete all 10 quizzes to unlock bonus")
        topic_id = pack['bonus_topic_id']
    else:
        topic_id = pack['quiz_topic_ids'][quiz_index]
    
    # Get topic
    topic = topics_col.find_one({'_id': ObjectId(topic_id)})
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get questions with randomized options
    next_attempt = attempt_count + 1
    questions = get_quiz_questions(topic_id, next_attempt)
    
    # Remove correct_key from questions (only show after 3rd attempt)
    for q in questions:
        q.pop('correct_key', None)
    
    return {
        'quiz_index': quiz_index,
        'topic': serialize_doc(topic),
        'questions': questions,
        'attempt_number': next_attempt,
        'attempts_remaining': 3 - next_attempt
    }

@app.post("/api/quizzes/{quiz_index}/submit")
def submit_quiz(
    quiz_index: int,
    data: QuizSubmit,
    current_user: Dict = Depends(get_current_user)
):
    if quiz_index < 0 or quiz_index > 10:
        raise HTTPException(status_code=400, detail="Quiz index must be 0-10")
    
    user_id = current_user['_id']
    today = date.today()
    
    # Check if quiz is locked
    if is_quiz_locked(user_id, today, quiz_index):
        raise HTTPException(status_code=403, detail="Quiz is locked after viewing answers")
    
    # Get attempt count
    attempt_count = get_attempt_count(user_id, today, quiz_index)
    
    if attempt_count >= 3:
        raise HTTPException(status_code=403, detail="Maximum 3 attempts reached")
    
    # Validate answer count (should be 3 questions)
    if len(data.answers) != 3:
        raise HTTPException(status_code=400, detail="Must answer exactly 3 questions")
    
    # Record attempt
    next_attempt = attempt_count + 1
    result = record_attempt(
        user_id=user_id,
        pack_date=today,
        quiz_index=quiz_index,
        attempt_num=next_attempt,
        answers=[a.dict() for a in data.answers],
        time_ms=data.time_ms
    )
    
    # Update user stats
    users_col.update_one(
        {'_id': ObjectId(user_id)},
        {'$inc': {'stats.quizzes_played': 1}}
    )
    
    # Get leaderboard rank
    leaderboard = compute_leaderboard(today, quiz_index)
    rank = None
    for idx, entry in enumerate(leaderboard):
        if entry['user_id'] == user_id:
            rank = entry['rank']
            break
    
    return {
        'attempt_number': next_attempt,
        'score': result['score'],
        'is_best': result['is_best'],
        'rank': rank,
        'attempts_remaining': 3 - next_attempt,
        'can_view_answers': next_attempt >= 3
    }

@app.get("/api/quizzes/{quiz_index}/answers")
def get_quiz_answers(
    quiz_index: int,
    current_user: Dict = Depends(get_current_user)
):
    user_id = current_user['_id']
    today = date.today()
    
    # Must have completed 3 attempts
    attempt_count = get_attempt_count(user_id, today, quiz_index)
    if attempt_count < 3:
        raise HTTPException(status_code=403, detail="Complete 3 attempts to view answers")
    
    # Get pack and topic
    pack = generate_daily_pack(today)
    
    if quiz_index == 10:
        topic_id = pack['bonus_topic_id']
    else:
        topic_id = pack['quiz_topic_ids'][quiz_index]
    
    # Get questions with correct answers
    questions = get_quiz_questions(topic_id, attempt_num=1)
    
    # Get user's last attempt answers
    last_attempt = attempts_col.find_one(
        {
            'user_id': ObjectId(user_id),
            'date': today.isoformat(),
            'quiz_index': quiz_index,
            'attempt_num': attempt_count
        }
    )
    
    user_answers = {}
    if last_attempt:
        for ans in last_attempt.get('answers', []):
            user_answers[ans['question_id']] = ans['choice_key']
    
    # Add user's answer and correctness to each question
    for q in questions:
        q['user_answer'] = user_answers.get(q['_id'])
        q['is_correct'] = q['user_answer'] == q['correct_key'] if q['user_answer'] else False
    
    return {'questions': questions}

@app.post("/api/quizzes/{quiz_index}/lock")
def lock_quiz(
    quiz_index: int,
    current_user: Dict = Depends(get_current_user)
):
    user_id = current_user['_id']
    today = date.today()
    
    # Must have completed 3 attempts
    attempt_count = get_attempt_count(user_id, today, quiz_index)
    if attempt_count < 3:
        raise HTTPException(status_code=403, detail="Complete 3 attempts before locking")
    
    # Lock the quiz
    success = lock_quiz_after_answers(user_id, today, quiz_index)
    
    return {'success': success, 'locked': True}

@app.get("/api/quizzes/{quiz_index}/leaderboard")
def get_quiz_leaderboard(
    quiz_index: int,
    group_id: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user)
):
    today = date.today()
    
    leaderboard = compute_leaderboard(today, quiz_index, group_id)
    
    return {
        'date': today.isoformat(),
        'quiz_index': quiz_index,
        'leaderboard': leaderboard,
        'current_user_id': current_user['_id']
    }

# ============================================================================
# USER - GROUPS
# ============================================================================

@app.get("/api/groups")
def get_my_groups(current_user: Dict = Depends(get_current_user)):
    user_id = ObjectId(current_user['_id'])
    
    groups = list(groups_col.find({
        'members': user_id
    }))
    
    for group in groups:
        group['member_count'] = len(group.get('members', []))
    
    return {'groups': serialize_doc(groups)}

@app.post("/api/groups")
def create_group(data: GroupCreate, current_user: Dict = Depends(get_current_user)):
    import random
    import string
    
    user_id = ObjectId(current_user['_id'])
    
    # Generate unique code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
    
    group_doc = {
        'name': data.name,
        'code': code,
        'owner_id': user_id,
        'members': [user_id],
        'created_at': datetime.utcnow()
    }
    
    result = groups_col.insert_one(group_doc)
    group_doc['_id'] = result.inserted_id
    group_doc['member_count'] = 1
    
    return {'group': serialize_doc(group_doc)}

@app.post("/api/groups/join")
def join_group(data: GroupJoin, current_user: Dict = Depends(get_current_user)):
    user_id = ObjectId(current_user['_id'])
    
    group = groups_col.find_one({'code': data.code.upper()})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if already a member
    if user_id in group.get('members', []):
        raise HTTPException(status_code=400, detail="Already a member of this group")
    
    # Add member
    groups_col.update_one(
        {'_id': group['_id']},
        {'$push': {'members': user_id}}
    )
    
    group = groups_col.find_one({'_id': group['_id']})
    group['member_count'] = len(group.get('members', []))
    
    return {'group': serialize_doc(group)}

@app.get("/api/groups/{group_id}/members")
def get_group_members(group_id: str, current_user: Dict = Depends(get_current_user)):
    group = groups_col.find_one({'_id': ObjectId(group_id)})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user is member
    if ObjectId(current_user['_id']) not in group.get('members', []):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    members = []
    for member_id in group.get('members', []):
        user = users_col.find_one({'_id': member_id})
        if user:
            members.append({
                '_id': str(user['_id']),
                'nickname': user['nickname'],
                'avatar_seed': user.get('avatar_seed', 'U')
            })
    
    return {'members': members}

@app.get("/api/groups/{group_id}/leaderboard")
def get_group_leaderboard(
    group_id: str,
    quiz_index: int = Query(...),
    current_user: Dict = Depends(get_current_user)
):
    group = groups_col.find_one({'_id': ObjectId(group_id)})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user is member
    if ObjectId(current_user['_id']) not in group.get('members', []):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    today = date.today()
    leaderboard = compute_leaderboard(today, quiz_index, group_id)
    
    return {
        'group_name': group['name'],
        'leaderboard': leaderboard
    }

# ============================================================================
# USER - PROFILE
# ============================================================================

@app.get("/api/profile")
def get_profile(current_user: Dict = Depends(get_current_user)):
    user_id = ObjectId(current_user['_id'])
    
    # Calculate stats
    total_attempts = attempts_col.count_documents({'user_id': user_id})
    
    attempts = list(attempts_col.find({'user_id': user_id}))
    avg_correct = 0
    if attempts:
        avg_correct = sum(a.get('percentage', 0) for a in attempts) / len(attempts)
    
    # Get personal best
    best_result = results_col.find_one(
        {'user_id': user_id},
        sort=[('best_pct', DESCENDING), ('best_time_ms', ASCENDING)]
    )
    
    personal_best = 0
    if best_result:
        personal_best = best_result.get('best_pct', 0)
    
    return {
        'user': current_user,
        'stats': {
            'quizzes_played': total_attempts,
            'avg_correct': round(avg_correct, 1),
            'personal_best': round(personal_best, 1)
        },
        'badges': current_user.get('badges', [])
    }

# ============================================================================
# INITIALIZATION
# ============================================================================

@app.on_event("startup")
async def startup_event():
    # Create admin user if not exists
    admin = users_col.find_one({'email': 'admin@socraquest.sk'})
    if not admin:
        admin_doc = {
            'email': 'admin@socraquest.sk',
            'password_hash': hash_password('Welcome@123##'),
            'nickname': 'Admin',
            'role': 'admin',
            'avatar_seed': 'A',
            'stats': {'quizzes_played': 0, 'avg_correct': 0, 'personal_best': 0},
            'badges': [],
            'created_at': datetime.utcnow()
        }
        users_col.insert_one(admin_doc)
        print("✅ Admin user created: admin@socraquest.sk")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "SocraQuest API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
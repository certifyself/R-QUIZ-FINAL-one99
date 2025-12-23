from fastapi import FastAPI, HTTPException, Depends, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from bson import ObjectId
import os
import jwt
import bcrypt
import pandas as pd
import io
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
    get_question_usage_stats,
    reset_question_usage,
    db,
    users_col,
    topics_col,
    questions_col,
    daily_packs_col,
    attempts_col,
    results_col,
    groups_col,
    ads_config_col,
    manual_ads_col,
    notification_settings_col,
    notification_logs_col,
    user_devices_col
)
from push_service import (
    send_push_notification,
    send_to_multiple_users,
    register_device_token,
    NOTIFICATION_TEMPLATES
)
from badge_service import (
    check_and_award_badges,
    get_user_badges,
    BADGES
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
    referral_code: Optional[str] = None

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

class BulkTopicOperation(BaseModel):
    topic_ids: List[str] = Field(min_items=1)


class QuestionOption(BaseModel):
    key: str  # A, B, C, D
    label: Any  # Can be string or dict {en: str, sk: str}

class QuestionCreate(BaseModel):
    topic_id: str
    text: Any  # Can be string or dict {en: str, sk: str}
    options: List[QuestionOption] = Field(min_length=4, max_length=4)
    correct_key: str  # A, B, C, or D
    image_url: Optional[str] = None  # Optional image URL
    active: bool = True

class QuestionUpdate(BaseModel):
    topic_id: Optional[str] = None
    text: Optional[Any] = None  # Can be string or dict
    options: Optional[List[QuestionOption]] = None
    correct_key: Optional[str] = None
    image_url: Optional[str] = None
    active: Optional[bool] = None

class AnswerSubmit(BaseModel):
    question_id: str
    choice_key: str

class QuizSubmit(BaseModel):
    answers: List[AnswerSubmit]
    time_ms: int

class GroupCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)

class GroupJoin(BaseModel):
    code: str = Field(min_length=6, max_length=10)

class GroupInvite(BaseModel):
    group_id: str
    email: EmailStr
    message: Optional[str] = None

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


def _check_referral_badges(user_id: ObjectId, users_col):
    """Check and award referral badges"""
    user = users_col.find_one({'_id': user_id})
    if not user:
        return
    
    referral_count = user.get('referral_count', 0)
    earned_badges = user.get('badges', [])
    earned_badge_ids = [b['badge_id'] for b in earned_badges]
    
    from badge_service import _award_badge
    
    # Check each referral milestone
    if 'referrer_1' not in earned_badge_ids and referral_count >= 1:
        _award_badge(user_id, 'referrer_1', users_col)
    if 'referrer_5' not in earned_badge_ids and referral_count >= 5:
        _award_badge(user_id, 'referrer_5', users_col)
    if 'referrer_10' not in earned_badge_ids and referral_count >= 10:
        _award_badge(user_id, 'referrer_10', users_col)
    if 'referrer_25' not in earned_badge_ids and referral_count >= 25:
        _award_badge(user_id, 'referrer_25', users_col)


# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.post("/api/auth/register", response_model=TokenResponse)
def register(data: RegisterRequest):
    # Check if user exists
    if users_col.find_one({'email': data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate unique referral code for this user
    import secrets
    referral_code = secrets.token_urlsafe(8)[:8].upper()
    # Ensure uniqueness
    while users_col.find_one({'referral_code': referral_code}):
        referral_code = secrets.token_urlsafe(8)[:8].upper()
    
    # Check if referred by someone
    referred_by = None
    if data.referral_code:
        referrer = users_col.find_one({'referral_code': data.referral_code})
        if referrer:
            referred_by = referrer['_id']
    
    # Create user
    user_doc = {
        'email': data.email,
        'password_hash': hash_password(data.password),
        'nickname': data.nickname,
        'role': 'user',
        'avatar_seed': data.nickname[0].upper(),
        'referral_code': referral_code,
        'referred_by': referred_by,
        'referral_count': 0,
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
    
    # If referred, increment referrer's count and check for badges
    if referred_by:
        users_col.update_one(
            {'_id': referred_by},
            {'$inc': {'referral_count': 1}}
        )
        # Check for referral badges
        _check_referral_badges(referred_by, users_col)
    
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

@app.delete("/api/admin/topics/delete-all")
def delete_all_topics_and_questions(current_user: Dict = Depends(get_current_admin)):
    """Delete all topics and questions - USE WITH CAUTION"""
    try:
        # Delete all questions
        questions_result = questions_col.delete_many({})
        
        # Delete all topics
        topics_result = topics_col.delete_many({})
        
        # Delete all daily packs (they reference topics)
        packs_result = daily_packs_col.delete_many({})
        
        return {
            'success': True,
            'deleted_questions': questions_result.deleted_count,
            'deleted_topics': topics_result.deleted_count,
            'deleted_packs': packs_result.deleted_count,
            'message': 'All topics, questions, and daily packs have been deleted'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete data: {str(e)}")

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

@app.post("/api/admin/topics/bulk-delete")
def bulk_delete_topics_admin(data: BulkTopicOperation, current_user: Dict = Depends(get_current_admin)):
    """Delete multiple topics at once (including their questions)"""
    deleted_topics = 0
    deleted_questions = 0
    errors = []
    
    for topic_id in data.topic_ids:
        try:
            # First, delete all questions associated with this topic
            questions_result = questions_col.delete_many({'topic_id': ObjectId(topic_id)})
            deleted_questions += questions_result.deleted_count
            
            # Then delete the topic
            result = topics_col.delete_one({'_id': ObjectId(topic_id)})
            if result.deleted_count > 0:
                deleted_topics += 1
            else:
                errors.append({'topic_id': topic_id, 'error': 'Topic not found'})
        except Exception as e:
            errors.append({'topic_id': topic_id, 'error': str(e)})
    
    return {
        'success': True,
        'deleted_topics': deleted_topics,
        'deleted_questions': deleted_questions,
        'total_requested': len(data.topic_ids),
        'errors': errors
    }

@app.patch("/api/admin/topics/bulk-active")
def bulk_activate_topics_admin(data: BulkTopicOperation, current_user: Dict = Depends(get_current_admin)):
    """Mark multiple topics as active"""
    result = topics_col.update_many(
        {'_id': {'$in': [ObjectId(tid) for tid in data.topic_ids]}},
        {'$set': {'active': True, 'updated_at': datetime.utcnow()}}
    )
    
    return {
        'success': True,
        'updated_count': result.modified_count,
        'total_requested': len(data.topic_ids)
    }

@app.patch("/api/admin/topics/bulk-inactive")
def bulk_deactivate_topics_admin(data: BulkTopicOperation, current_user: Dict = Depends(get_current_admin)):
    """Mark multiple topics as inactive"""
    result = topics_col.update_many(
        {'_id': {'$in': [ObjectId(tid) for tid in data.topic_ids]}},
        {'$set': {'active': False, 'updated_at': datetime.utcnow()}}
    )
    
    return {
        'success': True,
        'updated_count': result.modified_count,
        'total_requested': len(data.topic_ids)
    }


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
    
    # Add image_url if provided
    if data.image_url:
        question_doc['image_url'] = data.image_url
    
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
# ADMIN - QUESTION USAGE TRACKING (NO-REPEAT SYSTEM)
# ============================================================================

@app.get("/api/admin/questions/usage-stats")
def get_usage_stats(current_user: Dict = Depends(get_current_admin)):
    """
    Get statistics about question usage for the no-repeat system.
    Shows how many questions have been used and how many remain.
    """
    stats = get_question_usage_stats()
    return {
        'success': True,
        'stats': stats,
        'info': 'Questions will not repeat until all questions have been used. System auto-resets when exhausted.'
    }


@app.post("/api/admin/questions/reset-usage")
def reset_usage_tracking(current_user: Dict = Depends(get_current_admin)):
    """
    Manually reset the question usage tracker.
    This allows all questions to be used again from scratch.
    Use this after uploading new questions or when you want to start fresh.
    """
    result = reset_question_usage()
    
    # Also delete today's pack so it regenerates with fresh questions
    today = date.today().isoformat()
    daily_packs_col.delete_one({'date': today})
    
    return {
        'success': True,
        'message': 'Question usage tracker reset. Today\'s pack will regenerate with fresh questions.',
        'action_taken': 'Deleted today\'s pack to force regeneration'
    }


# ============================================================================
# ADMIN - IMAGE UPLOAD
# ============================================================================

import base64
import uuid as uuid_module

# Directory to store uploaded images
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/admin/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_admin)
):
    """Upload an image and return its URL"""
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}")
    
    # Generate unique filename
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f"{uuid_module.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Save file
    contents = await file.read()
    with open(filepath, 'wb') as f:
        f.write(contents)
    
    # Return the URL (served by nginx or static files)
    image_url = f"/uploads/{filename}"
    
    return {
        'success': True,
        'image_url': image_url,
        'filename': filename
    }

from fastapi.staticfiles import StaticFiles

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ============================================================================
# ADMIN - BULK UPLOAD
# ============================================================================

@app.get("/api/admin/questions/template")
def download_excel_template(current_user: Dict = Depends(get_current_admin)):
    """Download Excel template for bulk question upload (NEW FORMAT)"""
    # Create sample template with new column format
    template_data = {
        'topic_sk': ['História', 'Geografia', 'Veda'],
        'topic_en': ['History', 'Geography', 'Science'],
        'question_sk': [
            'V ktorom roku skončila druhá svetová vojna?',
            'Aké je hlavné mesto Francúzska?',
            'Aká je chemická značka pre vodu?'
        ],
        'question_en': [
            'In which year did World War II end?',
            'What is the capital of France?',
            'What is the chemical symbol for water?'
        ],
        'a_sk': ['1943', 'Londýn', 'H2O'],
        'b_sk': ['1945', 'Berlín', 'CO2'],
        'c_sk': ['1947', 'Madrid', 'O2'],
        'd_sk': ['1950', 'Paríž', 'N2'],
        'a_en': ['1943', 'London', 'H2O'],
        'b_en': ['1945', 'Berlin', 'CO2'],
        'c_en': ['1947', 'Madrid', 'O2'],
        'd_en': ['1950', 'Paris', 'N2'],
        'correct': ['B', 'D', 'A'],
        'image': ['', 'yes', '']  # Leave empty or put 'yes' to mark for image, or put full URL
    }
    
    df = pd.DataFrame(template_data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Questions')
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=socraquest_questions_template.xlsx'}
    )


@app.get("/api/admin/image-quiz/template")
def download_image_quiz_template(current_user: Dict = Depends(get_current_admin)):
    """Download Excel template for image quiz bulk upload"""
    template_data = {
        'question_sk': [
            'Ktorá slávna pamiatka je zobrazená?',
            'Aká budova je na obrázku?',
            'Ktoré zviera vidíte?'
        ],
        'question_en': [
            'Which famous landmark is shown?',
            'What building is in the picture?',
            'Which animal do you see?'
        ],
        'image_prompt': [
            'Eiffel Tower in Paris, France',
            'Colosseum in Rome, Italy',
            'African elephant in savanna'
        ],
        'a_sk': ['Eiffelova veža', 'Koloseum', 'Slon'],
        'b_sk': ['Big Ben', 'Parthenon', 'Lev'],
        'c_sk': ['Socha slobody', 'Pyramída', 'Žirafa'],
        'd_sk': ['Pisa veža', 'Taj Mahal', 'Zebra'],
        'a_en': ['Eiffel Tower', 'Colosseum', 'Elephant'],
        'b_en': ['Big Ben', 'Parthenon', 'Lion'],
        'c_en': ['Statue of Liberty', 'Pyramid', 'Giraffe'],
        'd_en': ['Leaning Tower of Pisa', 'Taj Mahal', 'Zebra'],
        'correct': ['A', 'A', 'A']
    }
    
    df = pd.DataFrame(template_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Image Quiz')
        
        # Add instructions sheet
        instructions = pd.DataFrame({
            'Instructions': [
                'Image Quiz Template - Questions with AI-Generated Images',
                '',
                'Columns:',
                '- question_sk: Question text in Slovak',
                '- question_en: Question text in English',
                '- image_prompt: Description for AI to generate the image (be specific!)',
                '- a_sk, b_sk, c_sk, d_sk: Answer options in Slovak',
                '- a_en, b_en, c_en, d_en: Answer options in English',
                '- correct: Correct answer (A, B, C, or D)',
                '',
                'Tips for image_prompt:',
                '- Be specific: "Eiffel Tower in Paris at sunset" is better than "a tower"',
                '- Include context: "African elephant in savanna" not just "elephant"',
                '- Avoid text in images: AI will generate visual content only'
            ]
        })
        instructions.to_excel(writer, index=False, sheet_name='Instructions')
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=socraquest_image_quiz_template.xlsx'}
    )


@app.post("/api/admin/image-quiz/bulk-upload")
async def bulk_upload_image_quiz(
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_admin)
):
    """
    Bulk upload image quiz questions from Excel file.
    AI will automatically generate images based on the 'image_prompt' column.
    """
    from image_service import generate_quiz_image
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be Excel format (.xlsx or .xls)")
    
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Validate required columns
        required_cols = [
            'question_sk', 'question_en', 'image_prompt',
            'a_sk', 'b_sk', 'c_sk', 'd_sk',
            'a_en', 'b_en', 'c_en', 'd_en',
            'correct'
        ]
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_cols)}"
            )
        
        # Find or create "Image Quiz" topic
        image_topic = topics_col.find_one({'name': 'Image Quiz'})
        if not image_topic:
            result = topics_col.insert_one({
                'name': 'Image Quiz',
                'name_sk': 'Obrázkový kvíz',
                'active': True,
                'created_at': datetime.utcnow()
            })
            topic_id = result.inserted_id
        else:
            topic_id = image_topic['_id']
        
        imported_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Get the image prompt
                image_prompt = str(row['image_prompt']).strip()
                if not image_prompt or image_prompt == 'nan':
                    errors.append(f"Row {idx + 2}: Missing image_prompt")
                    continue
                
                # Generate image using AI
                print(f"🎨 Generating image for row {idx + 2}: {image_prompt[:50]}...")
                image_url = await generate_quiz_image(image_prompt, "Image Quiz")
                
                if not image_url:
                    errors.append(f"Row {idx + 2}: Failed to generate image for '{image_prompt[:30]}...'")
                    continue
                
                # Create the question
                question_doc = {
                    'topic_id': topic_id,
                    'text': {
                        'en': str(row['question_en']).strip(),
                        'sk': str(row['question_sk']).strip()
                    },
                    'options': [
                        {'key': 'A', 'label': {'en': str(row['a_en']).strip(), 'sk': str(row['a_sk']).strip()}},
                        {'key': 'B', 'label': {'en': str(row['b_en']).strip(), 'sk': str(row['b_sk']).strip()}},
                        {'key': 'C', 'label': {'en': str(row['c_en']).strip(), 'sk': str(row['c_sk']).strip()}},
                        {'key': 'D', 'label': {'en': str(row['d_en']).strip(), 'sk': str(row['d_sk']).strip()}}
                    ],
                    'correct_key': str(row['correct']).strip().upper(),
                    'image_url': image_url,
                    'image_prompt': image_prompt,  # Store the prompt for reference
                    'active': True,
                    'created_at': datetime.utcnow()
                }
                
                questions_col.insert_one(question_doc)
                imported_count += 1
                print(f"✅ Imported question {imported_count}: {row['question_en'][:40]}...")
                
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
        
        # Update topic question count
        q_count = questions_col.count_documents({'topic_id': topic_id})
        topics_col.update_one({'_id': topic_id}, {'$set': {'question_count': q_count}})
        
        return {
            'success': True,
            'imported': imported_count,
            'errors': errors,
            'message': f'Successfully imported {imported_count} image quiz questions with AI-generated images'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/admin/questions/bulk-upload")
async def bulk_upload_questions(
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_admin)
):
    """Bulk upload questions from Excel file"""
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be Excel format (.xlsx or .xls)")
    
    try:
        # Read Excel file
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Validate required columns for new format
        required_cols = [
            'topic_sk', 'topic_en', 'question_sk', 'question_en',
            'a_sk', 'b_sk', 'c_sk', 'd_sk',
            'a_en', 'b_en', 'c_en', 'd_en',
            'correct'
        ]
        
        # image is optional
        optional_cols = ['image']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_cols)}"
            )
        
        # Process each row
        imported_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Get topic names (English and Slovak)
                topic_en = str(row['topic_en']).strip()
                topic_sk = str(row['topic_sk']).strip()
                
                # Find or create topic using English name as primary identifier
                topic = topics_col.find_one({'name': topic_en})
                
                if not topic:
                    # Create topic if doesn't exist
                    # Store English name as primary, Slovak in metadata
                    result = topics_col.insert_one({
                        'name': topic_en,
                        'name_sk': topic_sk,
                        'active': True,
                        'created_at': datetime.utcnow()
                    })
                    topic_id = result.inserted_id
                else:
                    topic_id = topic['_id']
                
                # Validate correct answer
                correct = str(row['correct']).strip().upper()
                if correct not in ['A', 'B', 'C', 'D']:
                    errors.append(f"Row {idx + 2}: Invalid correct answer '{correct}' (must be A, B, C, or D)")
                    continue
                
                # Build multilingual question
                question_doc = {
                    'topic_id': topic_id,
                    'text': {
                        'en': str(row['question_en']).strip(),
                        'sk': str(row['question_sk']).strip()
                    },
                    'options': [
                        {
                            'key': 'A',
                            'label': {
                                'en': str(row['a_en']).strip(),
                                'sk': str(row['a_sk']).strip()
                            }
                        },
                        {
                            'key': 'B',
                            'label': {
                                'en': str(row['b_en']).strip(),
                                'sk': str(row['b_sk']).strip()
                            }
                        },
                        {
                            'key': 'C',
                            'label': {
                                'en': str(row['c_en']).strip(),
                                'sk': str(row['c_sk']).strip()
                            }
                        },
                        {
                            'key': 'D',
                            'label': {
                                'en': str(row['d_en']).strip(),
                                'sk': str(row['d_sk']).strip()
                            }
                        }
                    ],
                    'correct_key': correct,
                    'active': True,
                    'created_at': datetime.utcnow()
                }
                
                # Add image if provided (check for 'yes' or actual URL)
                if 'image' in row and pd.notna(row['image']):
                    image_val = str(row['image']).strip().lower()
                    # If value is 'yes', mark for image but no URL yet
                    # If it's a URL (starts with http), use it
                    if image_val.startswith('http'):
                        question_doc['image_url'] = image_val
                    elif image_val == 'yes':
                        question_doc['has_image'] = True
                
                questions_col.insert_one(question_doc)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
        
        result_msg = f"Successfully imported {imported_count} questions"
        if errors:
            result_msg += f". {len(errors)} errors occurred."
        
        return {
            'success': True,
            'imported': imported_count,
            'errors': errors[:10],  # Return first 10 errors
            'message': result_msg
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process Excel file: {str(e)}")

# ============================================================================
# ADMIN - ADS MANAGEMENT
# ============================================================================

@app.get("/api/admin/ads/config")
def get_ad_config(current_user: Dict = Depends(get_current_admin)):
    """Get current ad configuration"""
    config = ads_config_col.find_one({'type': 'global'})
    if not config:
        # Return default config
        return {
            'google_adsense': {
                'enabled': False,
                'client_id': '',
                'banner_slot_id': '',
                'video_slot_id': ''
            },
            'taboola': {
                'enabled': False,
                'publisher_id': '',
                'placement_name': ''
            }
        }
    return serialize_doc(config)

@app.post("/api/admin/ads/config")
def update_ad_config(
    config_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_admin)
):
    """Update ad configuration"""
    config_data['type'] = 'global'
    config_data['updated_at'] = datetime.utcnow()
    
    result = ads_config_col.update_one(
        {'type': 'global'},
        {'$set': config_data},
        upsert=True
    )
    
    return {'success': True, 'message': 'Ad configuration updated successfully'}

@app.get("/api/ads/config")
def get_public_ad_config():
    """Get ad configuration for public use (without sensitive data)"""
    config = ads_config_col.find_one({'type': 'global'})
    if not config:
        return {'ads_enabled': False}
    
    return {
        'google_adsense': {
            'enabled': config.get('google_adsense', {}).get('enabled', False),
            'client_id': config.get('google_adsense', {}).get('client_id', ''),
            'banner_slot_id': config.get('google_adsense', {}).get('banner_slot_id', ''),
            'video_slot_id': config.get('google_adsense', {}).get('video_slot_id', '')
        },
        'taboola': {
            'enabled': config.get('taboola', {}).get('enabled', False),
            'publisher_id': config.get('taboola', {}).get('publisher_id', ''),
            'placement_name': config.get('taboola', {}).get('placement_name', '')
        }
    }

# ============================================================================
# ADMIN - MANUAL ADS
# ============================================================================

@app.get("/api/admin/ads/manual")
def get_manual_ads(current_user: Dict = Depends(get_current_admin)):
    """Get all manual ads"""
    ads = list(manual_ads_col.find())
    return {'ads': serialize_doc(ads)}

@app.post("/api/admin/ads/manual")
def create_manual_ad(
    ad_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_admin)
):
    """Create manual ad"""
    ad_doc = {
        'name': ad_data.get('name', 'Untitled Ad'),
        'type': ad_data.get('type', 'banner'),  # banner or video
        'image_url': ad_data.get('image_url', ''),
        'video_url': ad_data.get('video_url', ''),
        'click_url': ad_data.get('click_url', ''),
        'active': ad_data.get('active', True),
        'created_at': datetime.utcnow()
    }
    
    result = manual_ads_col.insert_one(ad_doc)
    ad_doc['_id'] = result.inserted_id
    
    return {'ad': serialize_doc(ad_doc)}

@app.put("/api/admin/ads/manual/{ad_id}")
def update_manual_ad(
    ad_id: str,
    ad_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_admin)
):
    """Update manual ad"""
    ad_data['updated_at'] = datetime.utcnow()
    
    result = manual_ads_col.update_one(
        {'_id': ObjectId(ad_id)},
        {'$set': ad_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    ad = manual_ads_col.find_one({'_id': ObjectId(ad_id)})
    return {'ad': serialize_doc(ad)}

@app.delete("/api/admin/ads/manual/{ad_id}")
def delete_manual_ad(
    ad_id: str,
    current_user: Dict = Depends(get_current_admin)
):
    """Delete manual ad"""
    result = manual_ads_col.delete_one({'_id': ObjectId(ad_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    return {'success': True}

@app.get("/api/ads/manual")
def get_active_manual_ads(ad_type: str = Query('banner')):
    """Get active manual ads for public use"""
    ads = list(manual_ads_col.find({
        'active': True,
        'type': ad_type
    }))
    return {'ads': serialize_doc(ads)}

# ============================================================================
# PUSH NOTIFICATIONS
# ============================================================================

@app.post("/api/notifications/register-device")
def register_device(
    device_data: Dict[str, str],
    current_user: Dict = Depends(get_current_user)
):
    """Register user's device token for push notifications"""
    fcm_token = device_data.get('fcm_token')
    platform = device_data.get('platform', 'web')
    
    if not fcm_token:
        raise HTTPException(status_code=400, detail="fcm_token required")
    
    register_device_token(current_user['_id'], fcm_token, platform)
    
    return {'success': True, 'message': 'Device registered successfully'}

@app.get("/api/notifications/settings")
def get_notification_settings(current_user: Dict = Depends(get_current_user)):
    """Get user's notification preferences"""
    settings = notification_settings_col.find_one({'user_id': ObjectId(current_user['_id'])})
    
    if not settings:
        # Return default settings
        return {
            'enabled': True,
            'preferred_time': '09:00',
            'categories_enabled': {
                'daily_reminders': True,
                'streak_alerts': True,
                'leaderboard_updates': True,
                'rewards': True
            }
        }
    
    return serialize_doc(settings)

@app.post("/api/notifications/settings")
def update_notification_settings(
    settings_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Update user's notification preferences"""
    settings_data['user_id'] = ObjectId(current_user['_id'])
    settings_data['updated_at'] = datetime.utcnow()
    
    notification_settings_col.update_one(
        {'user_id': ObjectId(current_user['_id'])},
        {'$set': settings_data},
        upsert=True
    )
    
    return {'success': True, 'message': 'Notification settings updated'}

# ============================================================================
# ADMIN - PUSH NOTIFICATIONS
# ============================================================================

@app.get("/api/admin/notifications/templates")
def get_notification_templates(current_user: Dict = Depends(get_current_admin)):
    """Get all notification templates"""
    return {'templates': NOTIFICATION_TEMPLATES}

@app.post("/api/admin/notifications/send")
def send_manual_notification(
    notification_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_admin)
):
    """Send manual notification to users"""
    title = notification_data.get('title')
    body = notification_data.get('body')
    target = notification_data.get('target', 'all')  # all, active, inactive
    
    if not title or not body:
        raise HTTPException(status_code=400, detail="title and body required")
    
    # Get target users
    if target == 'all':
        users = list(users_col.find({'role': 'user'}, {'_id': 1}))
    elif target == 'active':
        # Users who played in last 7 days
        from datetime import timedelta
        week_ago = (datetime.utcnow() - timedelta(days=7))
        active_user_ids = attempts_col.distinct('user_id', {
            'finished_at': {'$gte': week_ago}
        })
        users = [{'_id': uid} for uid in active_user_ids]
    else:
        users = []
    
    user_ids = [str(u['_id']) for u in users]
    
    # Check how many users have registered devices
    registered_devices = user_devices_col.count_documents({
        'user_id': {'$in': [u['_id'] for u in users]},
        'active': True
    })
    
    # Send to all users
    result = send_to_multiple_users(
        user_ids,
        title,
        body,
        'marketing',
        notification_data.get('data')
    )
    
    return {
        'success': True,
        'total_users': result['total_users'],
        'registered_devices': registered_devices,
        'delivered': result['delivered'],
        'failed': result['failed'],
        'message': f"Sent to {result['delivered']} users. {registered_devices} of {len(users)} users have push notifications enabled."
    }

@app.get("/api/admin/notifications/logs")
def get_notification_logs(
    limit: int = Query(50, le=200),
    current_user: Dict = Depends(get_current_admin)
):
    """Get recent notification logs"""
    logs = list(notification_logs_col.find().sort('sent_at', -1).limit(limit))
    
    # Add user info
    for log in logs:
        user = users_col.find_one({'_id': log['user_id']})
        log['user_nickname'] = user['nickname'] if user else 'Unknown'
    
    return {'logs': serialize_doc(logs)}

@app.get("/api/admin/notifications/stats")
def get_notification_stats(current_user: Dict = Depends(get_current_admin)):
    """Get notification analytics"""
    total_sent = notification_logs_col.count_documents({})
    
    # Aggregate stats
    pipeline = [
        {
            '$group': {
                '_id': '$type',
                'count': {'$sum': 1},
                'total_delivered': {'$sum': '$delivered_count'},
                'total_failed': {'$sum': '$failed_count'}
            }
        }
    ]
    
    stats_by_type = list(notification_logs_col.aggregate(pipeline))
    
    return {
        'total_sent': total_sent,
        'stats_by_type': stats_by_type
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
    for quiz_data in pack['quizzes'][:10]:  # First 10 are regular
        idx = quiz_data['index']
        
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
        
        # Get topic names for this quiz
        topic_names = []
        for topic_id in quiz_data['topic_ids']:
            topic = topics_col.find_one({'_id': ObjectId(topic_id)})
            if topic:
                topic_names.append(topic['name'])
        
        quizzes.append({
            'index': idx,
            'topic_count': len(quiz_data['topic_ids']),
            'topic_names': topic_names,
            'attempt_count': attempt_count,
            'is_locked': is_locked,
            'best_score': best_score,
            'status': 'locked' if is_locked else ('completed' if attempt_count >= 3 else ('in_progress' if attempt_count > 0 else 'available'))
        })
    
    # Bonus quiz (index 10)
    bonus_data = pack['quizzes'][10]
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
    
    # Bonus unlocks when all 10 regular quizzes attempted at least once
    all_completed = all(q['attempt_count'] > 0 for q in quizzes)
    
    bonus_topic_names = []
    for topic_id in bonus_data['topic_ids']:
        topic = topics_col.find_one({'_id': ObjectId(topic_id)})
        if topic:
            bonus_topic_names.append(topic['name'])
    
    bonus_quiz = {
        'index': 10,
        'topic_count': len(bonus_data['topic_ids']),
        'topic_names': bonus_topic_names,
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
    
    # Get quiz data
    quiz_data = pack['quizzes'][quiz_index]
    topic_ids = quiz_data['topic_ids']
    
    # Check bonus unlock
    if quiz_index == 10:
        regular_attempts = [get_attempt_count(user_id, today, i) for i in range(10)]
        if not all(count > 0 for count in regular_attempts):
            raise HTTPException(status_code=403, detail="Complete all 10 quizzes to unlock bonus")
    
    # Get questions with randomized options (30 questions from 10 topics)
    # Pass pack_date and quiz_index to use pre-selected questions (no-repeat logic)
    next_attempt = attempt_count + 1
    questions = get_quiz_questions(topic_ids, next_attempt, lang, pack_date=today, quiz_index=quiz_index)
    
    # Remove correct_key from questions (only show after viewing answers)
    for q in questions:
        q.pop('correct_key', None)
    
    return {
        'quiz_index': quiz_index,
        'topic_count': len(topic_ids),
        'questions': questions,
        'total_questions': len(questions),
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
    
    # Validate answer count (should be 30 questions now)
    # Allow submission even if some are unanswered (marked as 'UNANSWERED')
    if len(data.answers) != 30:
        raise HTTPException(status_code=400, detail="Must submit exactly 30 answers")
    
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
    
    # Auto-lock quiz after 3rd attempt
    if next_attempt >= 3:
        lock_quiz_after_answers(user_id, today, quiz_index)
    
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
    
    # Check if perfect score
    is_perfect = result['score']['percentage'] == 100
    
    # Check and award badges
    newly_earned_badges = check_and_award_badges(
        user_id=ObjectId(user_id),
        quiz_index=quiz_index,
        score=result['score']['correct_count'],
        time_ms=data.time_ms,
        users_col=users_col,
        results_col=results_col,
        daily_packs_col=daily_packs_col
    )
    
    return {
        'attempt_number': next_attempt,
        'score': result['score'],
        'is_best': result['is_best'],
        'rank': rank,
        'attempts_remaining': 3 - next_attempt,
        'can_view_answers': True,  # Can always view answers after submitting
        'is_perfect': is_perfect,
        'quiz_locked': next_attempt >= 3,  # Quiz locked after 3rd attempt
        'badges_earned': newly_earned_badges  # New badges earned from this quiz
    }

@app.get("/api/quizzes/{quiz_index}/answers")
def get_quiz_answers(
    quiz_index: int,
    lang: str = Query('en', regex='^(en|sk)$'),
    current_user: Dict = Depends(get_current_user)
):
    user_id = current_user['_id']
    today = date.today()
    
    # Can view answers after any attempt (warning shown in frontend for attempts < 3)
    attempt_count = get_attempt_count(user_id, today, quiz_index)
    if attempt_count < 1:
        raise HTTPException(status_code=403, detail="Complete at least 1 attempt to view answers")
    
    # Get pack and quiz data
    pack = generate_daily_pack(today)
    quiz_data = pack['quizzes'][quiz_index]
    topic_ids = quiz_data['topic_ids']
    
    # Get questions with correct answers (30 questions)
    # Pass pack_date and quiz_index to use pre-selected questions
    questions = get_quiz_questions(topic_ids, attempt_num=1, language=lang, pack_date=today, quiz_index=quiz_index)
    
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
    apply_penalty: bool = False,  # Kept for backwards compatibility but IGNORED
    current_user: Dict = Depends(get_current_user)
):
    user_id = current_user['_id']
    today = date.today()
    
    # Lock the quiz - NO PENALTY APPLIED
    # Users can view correct answers without losing their score
    success = lock_quiz_after_answers(user_id, today, quiz_index)
    
    return {'success': success, 'locked': True, 'penalty_applied': False}

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


@app.get("/api/rankings/daily")
def get_daily_overall_leaderboard(
    group_id: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get overall daily challenge leaderboard.
    Rankings based on: total percentage across all completed quizzes, then total time.
    """
    today = date.today()
    today_str = today.isoformat()
    
    # Build filter
    query = {'date': today_str}
    
    # Filter by group if provided
    if group_id:
        group = groups_col.find_one({'_id': ObjectId(group_id)})
        if group and 'members' in group:
            query['user_id'] = {'$in': group['members']}
    
    # Aggregate results per user for today
    pipeline = [
        {'$match': query},
        {'$group': {
            '_id': '$user_id',
            'total_pct': {'$sum': '$best_pct'},
            'total_time_ms': {'$sum': '$best_time_ms'},
            'quizzes_completed': {'$sum': 1},
            'avg_pct': {'$avg': '$best_pct'}
        }},
        {'$sort': {'avg_pct': -1, 'total_time_ms': 1}}
    ]
    
    aggregated = list(results_col.aggregate(pipeline))
    
    leaderboard = []
    for idx, entry in enumerate(aggregated):
        user = users_col.find_one({'_id': entry['_id']})
        
        leaderboard.append({
            'rank': idx + 1,
            'user_id': str(entry['_id']),
            'nickname': user['nickname'] if user else 'Unknown',
            'quizzes_completed': entry['quizzes_completed'],
            'avg_percentage': round(entry['avg_pct'], 2),
            'total_percentage': round(entry['total_pct'], 2),
            'total_time_ms': entry['total_time_ms']
        })
    
    return {
        'date': today_str,
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
        # Get member details (nicknames)
        member_details = []
        for member_id in group.get('members', []):
            member = users_col.find_one({'_id': member_id})
            if member:
                member_details.append({
                    '_id': str(member_id),
                    'nickname': member.get('nickname', 'Unknown'),
                    'is_owner': member_id == group.get('owner_id')
                })
        group['member_details'] = member_details
    
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


@app.post("/api/groups/{group_id}/invite")
def send_group_invite(
    group_id: str,
    invite: GroupInvite,
    current_user: Dict = Depends(get_current_user)
):
    """Send email invitation to join a group"""
    # Verify group exists and user is a member
    group = groups_col.find_one({'_id': ObjectId(group_id)})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if sender is member
    if ObjectId(current_user['_id']) not in group.get('members', []):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    # For now, we'll just return the invite details
    # In production, you would integrate with an email service (SendGrid, AWS SES, etc.)
    invite_url = f"https://mindgames-19.preview.emergentagent.com/groups/join/{group['code']}"
    
    # TODO: Send actual email using email service
    # For now, return the details that would be sent
    return {
        'success': True,
        'message': f'Invitation details prepared (email service not configured)',
        'invite_details': {
            'to': invite.email,
            'group_name': group['name'],
            'group_code': group['code'],
            'invite_url': invite_url,
            'invited_by': current_user['nickname'],
            'custom_message': invite.message
        }
    }


# ============================================================================
# USER - PROFILE
# ============================================================================

@app.get("/api/profile")
def get_profile(current_user: Dict = Depends(get_current_user)):
    user_id = ObjectId(current_user['_id'])
    user = users_col.find_one({'_id': user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user stats
    total_quizzes = results_col.count_documents({'user_id': user_id})
    
    # Get unique quizzes completed
    unique_quizzes = len(results_col.distinct('quiz_index', {'user_id': user_id}))
    
    # Get best score
    best_result = results_col.find_one(
        {'user_id': user_id},
        sort=[('best_pct', -1)]
    )
    best_score_pct = best_result['best_pct'] if best_result else 0
    
    # Get badges count
    badges_count = len(user.get('badges', []))
    
    return {
        'nickname': user['nickname'],
        'email': user['email'],
        'avatar_seed': user.get('avatar_seed', user['nickname'][0].upper()),
        'referral_code': user.get('referral_code', ''),
        'stats': {
            'total_quizzes': total_quizzes,
            'unique_quizzes': unique_quizzes,
            'best_score': best_score_pct
        },
        'badges_count': badges_count,
        'created_at': user.get('created_at')
    }


@app.get("/api/referrals")
def get_referral_stats(current_user: Dict = Depends(get_current_user)):
    """Get user's referral statistics"""
    user_id = ObjectId(current_user['_id'])
    user = users_col.find_one({'_id': user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    referral_code = user.get('referral_code', '')
    referral_count = user.get('referral_count', 0)
    
    # Get list of referred users
    referred_users = list(users_col.find(
        {'referred_by': user_id},
        {'nickname': 1, 'created_at': 1, 'stats': 1}
    ).sort('created_at', -1).limit(50))
    
    return {
        'referral_code': referral_code,
        'referral_count': referral_count,
        'referred_users': [serialize_doc(u) for u in referred_users],
        'invite_url': f"https://mindgames-19.preview.emergentagent.com/auth?ref={referral_code}"
    }

    
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


@app.get("/api/badges")
def get_badges(current_user: Dict = Depends(get_current_user)):
    """Get user's badge progress"""
    user_id = ObjectId(current_user['_id'])
    return get_user_badges(user_id, users_col)

@app.get("/api/badges/all")
def get_all_badges():
    """Get all available badge definitions"""
    return {'badges': list(BADGES.values())}


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
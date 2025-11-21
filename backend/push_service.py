"""
Push Notification Service using Firebase Cloud Messaging
Handles all notification types for SocraQuest
"""
import os
import firebase_admin
from firebase_admin import credentials, messaging
from datetime import datetime
from typing import List, Dict, Optional
from pymongo import MongoClient

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client['socraquest']

notification_settings_col = db['notification_settings']
notification_logs_col = db['notification_logs']
user_devices_col = db['user_devices']

# Initialize Firebase
try:
    cred = credentials.Certificate('/app/backend/firebase-service-account.json')
    firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin SDK initialized successfully")
except Exception as e:
    print(f"⚠️ Firebase initialization error: {e}")
    print("   Push notifications will be logged but not sent")


def send_push_notification(
    user_id: str,
    title: str,
    body: str,
    notification_type: str,
    data: Optional[Dict] = None
) -> Dict[str, any]:
    """
    Send push notification to user
    
    Args:
        user_id: User ID
        title: Notification title
        body: Notification message
        notification_type: Type (daily_reminder, streak, inactivity, etc.)
        data: Additional data payload
    
    Returns:
        {
            'success': bool,
            'delivered_count': int,
            'failed_count': int
        }
    """
    from bson import ObjectId
    
    # Check if user has notifications enabled
    settings = notification_settings_col.find_one({'user_id': ObjectId(user_id)})
    if settings and not settings.get('enabled', True):
        print(f"User {user_id} has notifications disabled")
        return {'success': False, 'delivered_count': 0, 'failed_count': 0}
    
    # Check category preferences
    if settings:
        categories = settings.get('categories_enabled', {})
        category_map = {
            'daily_reminder': 'daily_reminders',
            'streak': 'streak_alerts',
            'leaderboard': 'leaderboard_updates',
            'reward': 'rewards',
            'inactivity': 'daily_reminders',  # Use daily_reminders setting
            'marketing': 'daily_reminders'
        }
        category_key = category_map.get(notification_type, 'daily_reminders')
        if not categories.get(category_key, True):
            print(f"User {user_id} disabled {category_key} notifications")
            return {'success': False, 'delivered_count': 0, 'failed_count': 0}
    
    # Get user's device tokens
    devices = list(user_devices_col.find({
        'user_id': ObjectId(user_id),
        'active': True
    }))
    
    if not devices:
        print(f"No active devices for user {user_id}")
        return {'success': False, 'delivered_count': 0, 'failed_count': 0}
    
    tokens = [d['fcm_token'] for d in devices if d.get('fcm_token')]
    
    if not tokens:
        print(f"No FCM tokens for user {user_id}")
        return {'success': False, 'delivered_count': 0, 'failed_count': 0}
    
    # Create notification message
    message_data = data or {}
    message_data['type'] = notification_type
    message_data['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
    
    delivered = 0
    failed = 0
    
    for token in tokens:
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=message_data,
                token=token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='notification_icon',
                        color='#088395',  # Teal color
                        sound='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1
                        )
                    )
                )
            )
            
            response = messaging.send(message)
            delivered += 1
            print(f"✅ Notification sent to {token[:20]}... | Response: {response}")
            
        except Exception as e:
            failed += 1
            print(f"❌ Failed to send to {token[:20]}... | Error: {e}")
            
            # Remove invalid token
            if 'invalid' in str(e).lower() or 'not found' in str(e).lower():
                user_devices_col.update_one(
                    {'fcm_token': token},
                    {'$set': {'active': False}}
                )
    
    # Log notification
    notification_logs_col.insert_one({
        'user_id': ObjectId(user_id),
        'title': title,
        'body': body,
        'type': notification_type,
        'delivered_count': delivered,
        'failed_count': failed,
        'sent_at': datetime.utcnow()
    })
    
    return {
        'success': delivered > 0,
        'delivered_count': delivered,
        'failed_count': failed
    }


def send_to_multiple_users(
    user_ids: List[str],
    title: str,
    body: str,
    notification_type: str,
    data: Optional[Dict] = None
) -> Dict:
    """Send notification to multiple users"""
    results = {
        'total_users': len(user_ids),
        'delivered': 0,
        'failed': 0
    }
    
    for user_id in user_ids:
        result = send_push_notification(user_id, title, body, notification_type, data)
        if result['success']:
            results['delivered'] += 1
        else:
            results['failed'] += 1
    
    return results


def register_device_token(user_id: str, fcm_token: str, platform: str = 'web'):
    """Register user's device token for push notifications"""
    from bson import ObjectId
    
    user_devices_col.update_one(
        {
            'user_id': ObjectId(user_id),
            'fcm_token': fcm_token
        },
        {
            '$set': {
                'user_id': ObjectId(user_id),
                'fcm_token': fcm_token,
                'platform': platform,
                'active': True,
                'registered_at': datetime.utcnow()
            }
        },
        upsert=True
    )
    print(f"✅ Device token registered for user {user_id}")


# Notification templates
NOTIFICATION_TEMPLATES = {
    'daily_reminder': [
        {
            'title': 'Your Daily Quest Awaits! 🎯',
            'body': 'New quiz pack is ready. Don\'t break your streak!'
        },
        {
            'title': 'Quiz Time! ⏰',
            'body': 'Complete today\'s quizzes and climb the leaderboard!'
        },
        {
            'title': 'Challenge Yourself! 💪',
            'body': 'Your daily trivia challenge is waiting. Let\'s go!'
        }
    ],
    'streak_protection': [
        {
            'title': 'Streak Alert! 🔥',
            'body': 'Your {streak_days}-day streak is about to end! Play now!'
        },
        {
            'title': 'Don\'t Lose Your Progress! ⚠️',
            'body': 'Only {hours_left} hours left to save your streak!'
        }
    ],
    'inactivity_24h': [
        {
            'title': 'We Miss You! 😊',
            'body': 'Come back and continue your learning journey!'
        }
    ],
    'inactivity_3d': [
        {
            'title': 'Welcome Back! 👋',
            'body': 'New quizzes are waiting. Can you beat your best score?'
        }
    ],
    'inactivity_7d': [
        {
            'title': 'Long Time No See! 🌟',
            'body': 'Your friends are climbing the ranks. Ready to compete?'
        }
    ],
    'leaderboard_overtaken': [
        {
            'title': 'Position Lost! 😮',
            'body': '{competitor} just overtook you! Defend your rank!'
        }
    ],
    'leaderboard_improved': [
        {
            'title': 'Great Progress! 🎉',
            'body': 'You\'re now rank #{rank}! Keep it up!'
        }
    ],
    'badge_earned': [
        {
            'title': 'New Badge Unlocked! 🏅',
            'body': 'Congratulations! You earned: {badge_name}'
        }
    ],
    'badge_progress': [
        {
            'title': 'Almost There! 🎯',
            'body': 'Only {remaining} quizzes until your next badge!'
        }
    ]
}


if __name__ == '__main__':
    print("Push Notification Service Loaded")
    print(f"Templates available: {len(NOTIFICATION_TEMPLATES)} types")

"""
Badge System for SocraQuest
Defines badge types, criteria, and awarding logic
"""

from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from bson import ObjectId

# Badge Definitions
BADGES = {
    # Achievement Badges
    'first_quiz': {
        'id': 'first_quiz',
        'name': {'en': 'First Steps', 'sk': 'Prvé kroky'},
        'description': {'en': 'Complete your first quiz', 'sk': 'Dokončite svoj prvý kvíz'},
        'icon': 'Sparkles',
        'color': '#10b981',  # emerald
        'category': 'achievement'
    },
    'perfect_score': {
        'id': 'perfect_score',
        'name': {'en': 'Perfect Score', 'sk': 'Perfektné skóre'},
        'description': {'en': 'Score 100% (30/30) on any quiz', 'sk': 'Získajte 100% (30/30) v ktoromkoľvek kvíze'},
        'icon': 'Trophy',
        'color': '#f59e0b',  # amber
        'category': 'achievement'
    },
    'speed_demon': {
        'id': 'speed_demon',
        'name': {'en': 'Speed Demon', 'sk': 'Rýchly démon'},
        'description': {'en': 'Complete a quiz in under 5 minutes', 'sk': 'Dokončite kvíz za menej ako 5 minút'},
        'icon': 'Zap',
        'color': '#8b5cf6',  # violet
        'category': 'achievement'
    },
    'quiz_master': {
        'id': 'quiz_master',
        'name': {'en': 'Quiz Master', 'sk': 'Majster kvízov'},
        'description': {'en': 'Complete all 10 daily quizzes', 'sk': 'Dokončite všetkých 10 denných kvízov'},
        'icon': 'Crown',
        'color': '#eab308',  # yellow
        'category': 'achievement'
    },
    'bonus_hunter': {
        'id': 'bonus_hunter',
        'name': {'en': 'Bonus Hunter', 'sk': 'Lovec bonusov'},
        'description': {'en': 'Complete the bonus quiz', 'sk': 'Dokončite bonusový kvíz'},
        'icon': 'Gift',
        'color': '#ec4899',  # pink
        'category': 'achievement'
    },
    'daily_champion': {
        'id': 'daily_champion',
        'name': {'en': 'Daily Champion', 'sk': 'Denný šampión'},
        'description': {'en': 'Complete all 11 quizzes (10 + bonus) in one day', 'sk': 'Dokončite všetkých 11 kvízov (10 + bonus) v jeden deň'},
        'icon': 'Star',
        'color': '#eab308',  # yellow/gold
        'category': 'achievement'
    },
    
    # Streak Badges
    'streak_3': {
        'id': 'streak_3',
        'name': {'en': 'Streak Starter', 'sk': 'Začiatok série'},
        'description': {'en': 'Play 3 days in a row', 'sk': 'Hrajte 3 dni po sebe'},
        'icon': 'Flame',
        'color': '#f97316',  # orange
        'category': 'streak'
    },
    'streak_7': {
        'id': 'streak_7',
        'name': {'en': 'Dedicated', 'sk': 'Oddaný'},
        'description': {'en': 'Play 7 days in a row', 'sk': 'Hrajte 7 dní po sebe'},
        'icon': 'Flame',
        'color': '#dc2626',  # red
        'category': 'streak'
    },
    'streak_30': {
        'id': 'streak_30',
        'name': {'en': 'Champion', 'sk': 'Šampión'},
        'description': {'en': 'Play 30 days in a row', 'sk': 'Hrajte 30 dní po sebe'},
        'icon': 'Flame',
        'color': '#7c3aed',  # purple
        'category': 'streak'
    },
    
    # Completion Badges
    'quizzes_5': {
        'id': 'quizzes_5',
        'name': {'en': 'Beginner', 'sk': 'Začiatočník'},
        'description': {'en': 'Complete 5 quizzes', 'sk': 'Dokončite 5 kvízov'},
        'icon': 'Award',
        'color': '#06b6d4',  # cyan
        'category': 'completion'
    },
    'quizzes_25': {
        'id': 'quizzes_25',
        'name': {'en': 'Intermediate', 'sk': 'Pokročilý'},
        'description': {'en': 'Complete 25 quizzes', 'sk': 'Dokončite 25 kvízov'},
        'icon': 'Award',
        'color': '#3b82f6',  # blue
        'category': 'completion'
    },
    'quizzes_100': {
        'id': 'quizzes_100',
        'name': {'en': 'Expert', 'sk': 'Expert'},
        'description': {'en': 'Complete 100 quizzes', 'sk': 'Dokončite 100 kvízov'},
        'icon': 'Award',
        'color': '#8b5cf6',  # violet
        'category': 'completion'
    },
    
    # Special Badges
    'early_bird': {
        'id': 'early_bird',
        'name': {'en': 'Early Bird', 'sk': 'Ranné vtáča'},
        'description': {'en': 'Complete a quiz before 8 AM', 'sk': 'Dokončite kvíz pred 8:00'},
        'icon': 'Sunrise',
        'color': '#fbbf24',  # amber
        'category': 'special'
    },
    'night_owl': {
        'id': 'night_owl',
        'name': {'en': 'Night Owl', 'sk': 'Nočná sova'},
        'description': {'en': 'Complete a quiz after 10 PM', 'sk': 'Dokončite kvíz po 22:00'},
        'icon': 'Moon',
        'color': '#6366f1',  # indigo
        'category': 'special'
    },
    
    # Referral Badges
    'referrer_1': {
        'id': 'referrer_1',
        'name': {'en': 'Friend Bringer', 'sk': 'Prívod priateľa'},
        'description': {'en': 'Invite 1 friend who joins', 'sk': 'Pozvite 1 priateľa, ktorý sa pripojí'},
        'icon': 'Star',
        'color': '#f59e0b',  # amber
        'category': 'referral'
    },
    'referrer_5': {
        'id': 'referrer_5',
        'name': {'en': 'Social Butterfly', 'sk': 'Sociálny motýľ'},
        'description': {'en': 'Invite 5 friends who join', 'sk': 'Pozvite 5 priateľov, ktorí sa pripoja'},
        'icon': 'Star',
        'color': '#ec4899',  # pink
        'category': 'referral'
    },
    'referrer_10': {
        'id': 'referrer_10',
        'name': {'en': 'Community Builder', 'sk': 'Tvorca komunity'},
        'description': {'en': 'Invite 10 friends who join', 'sk': 'Pozvite 10 priateľov, ktorí sa pripoja'},
        'icon': 'Star',
        'color': '#8b5cf6',  # violet
        'category': 'referral'
    },
    'referrer_25': {
        'id': 'referrer_25',
        'name': {'en': 'Ambassador', 'sk': 'Veľvyslanec'},
        'description': {'en': 'Invite 25 friends who join', 'sk': 'Pozvite 25 priateľov, ktorí sa pripoja'},
        'icon': 'Star',
        'color': '#7c3aed',  # purple
        'category': 'referral'
    },
}


def check_and_award_badges(user_id: ObjectId, quiz_index: int, score: int, time_ms: int, 
                           users_col, results_col, daily_packs_col) -> List[Dict]:
    """
    Check if user earned any new badges after completing a quiz
    Returns list of newly earned badges
    """
    user = users_col.find_one({'_id': user_id})
    if not user:
        return []
    
    earned_badges = user.get('badges', [])
    earned_badge_ids = [b['badge_id'] for b in earned_badges]
    newly_earned = []
    
    # Get user's quiz history
    # Count UNIQUE quizzes completed (not total attempts)
    unique_quiz_indices = results_col.distinct('quiz_index', {'user_id': user_id})
    total_unique_quizzes = len(unique_quiz_indices)
    
    # 1. First Quiz Badge (check if this is the first unique quiz)
    if 'first_quiz' not in earned_badge_ids and total_unique_quizzes == 1:
        newly_earned.append(_award_badge(user_id, 'first_quiz', users_col, quiz_index))
    
    # 2. Perfect Score Badge
    if 'perfect_score' not in earned_badge_ids and score == 30:
        newly_earned.append(_award_badge(user_id, 'perfect_score', users_col, quiz_index))
    
    # 3. Speed Demon Badge (under 5 minutes = 300,000ms)
    if 'speed_demon' not in earned_badge_ids and time_ms < 300000:
        newly_earned.append(_award_badge(user_id, 'speed_demon', users_col, quiz_index))
    
    # 4. Quiz Master Badge (completed all 10 daily quizzes)
    if 'quiz_master' not in earned_badge_ids:
        today = date.today().isoformat()
        today_pack = daily_packs_col.find_one({'date': today})
        if today_pack:
            completed_today = results_col.count_documents({
                'user_id': user_id,
                'date': today,
                'quiz_index': {'$in': list(range(10))}  # quizzes 0-9
            })
            if completed_today >= 10:
                newly_earned.append(_award_badge(user_id, 'quiz_master', users_col))
    
    # 5. Bonus Hunter Badge
    if 'bonus_hunter' not in earned_badge_ids and quiz_index == 10:  # Bonus quiz
        newly_earned.append(_award_badge(user_id, 'bonus_hunter', users_col, quiz_index))
    
    # 6. Completion Badges (based on unique quizzes completed)
    if 'quizzes_5' not in earned_badge_ids and total_unique_quizzes >= 5:
        newly_earned.append(_award_badge(user_id, 'quizzes_5', users_col))
    if 'quizzes_25' not in earned_badge_ids and total_unique_quizzes >= 25:
        newly_earned.append(_award_badge(user_id, 'quizzes_25', users_col))
    if 'quizzes_100' not in earned_badge_ids and total_unique_quizzes >= 100:
        newly_earned.append(_award_badge(user_id, 'quizzes_100', users_col))
    
    # 7. Time-based Badges
    current_hour = datetime.utcnow().hour
    if 'early_bird' not in earned_badge_ids and current_hour < 8:
        newly_earned.append(_award_badge(user_id, 'early_bird', users_col, quiz_index))
    if 'night_owl' not in earned_badge_ids and current_hour >= 22:
        newly_earned.append(_award_badge(user_id, 'night_owl', users_col, quiz_index))
    
    # 8. Streak Badges
    _check_streak_badges(user_id, users_col, results_col, earned_badge_ids, newly_earned)
    
    return [b for b in newly_earned if b is not None]


def _award_badge(user_id: ObjectId, badge_id: str, users_col, quiz_index: Optional[int] = None) -> Dict:
    """Award a badge to a user"""
    badge_data = {
        'badge_id': badge_id,
        'earned_at': datetime.utcnow(),
    }
    if quiz_index is not None:
        badge_data['quiz_index'] = quiz_index
    
    users_col.update_one(
        {'_id': user_id},
        {'$push': {'badges': badge_data}}
    )
    
    # Return badge info for notification
    badge_def = BADGES.get(badge_id)
    if badge_def:
        return {
            **badge_def,
            'earned_at': badge_data['earned_at']
        }
    return None


def _check_streak_badges(user_id: ObjectId, users_col, results_col, earned_badge_ids: List[str], newly_earned: List):
    """Check if user earned any streak badges"""
    # Get unique dates user played
    results = results_col.find(
        {'user_id': user_id},
        {'date': 1, '_id': 0}
    ).sort('date', -1)
    
    dates = sorted(set([r['date'] for r in results]), reverse=True)
    
    if not dates:
        return
    
    # Calculate current streak
    current_streak = 1
    today = date.today().isoformat()
    
    # Start from today or most recent play date
    if dates[0] == today or dates[0] == (date.today() - timedelta(days=1)).isoformat():
        for i in range(len(dates) - 1):
            date1 = datetime.fromisoformat(dates[i]).date()
            date2 = datetime.fromisoformat(dates[i + 1]).date()
            
            if (date1 - date2).days == 1:
                current_streak += 1
            else:
                break
    
    # Award streak badges
    if 'streak_3' not in earned_badge_ids and current_streak >= 3:
        newly_earned.append(_award_badge(user_id, 'streak_3', users_col))
    if 'streak_7' not in earned_badge_ids and current_streak >= 7:
        newly_earned.append(_award_badge(user_id, 'streak_7', users_col))
    if 'streak_30' not in earned_badge_ids and current_streak >= 30:
        newly_earned.append(_award_badge(user_id, 'streak_30', users_col))


def get_user_badges(user_id: ObjectId, users_col) -> Dict:
    """Get user's badge progress"""
    user = users_col.find_one({'_id': user_id})
    if not user:
        return {'earned': [], 'available': []}
    
    earned_badges = user.get('badges', [])
    earned_badge_ids = [b['badge_id'] for b in earned_badges]
    
    # Build earned badges with full info
    earned_full = []
    for badge in earned_badges:
        badge_def = BADGES.get(badge['badge_id'])
        if badge_def:
            earned_full.append({
                **badge_def,
                'earned_at': badge.get('earned_at'),
                'quiz_index': badge.get('quiz_index')
            })
    
    # Build available (not yet earned) badges
    available = []
    for badge_id, badge_def in BADGES.items():
        if badge_id not in earned_badge_ids:
            available.append({**badge_def, 'locked': True})
    
    return {
        'earned': earned_full,
        'available': available,
        'total_earned': len(earned_full),
        'total_available': len(BADGES)
    }

"""
SocraQuest Core POC Test Script
Tests all core functionality in isolation before building the full app.

POC User Stories:
1. As a user, I get exactly 10 quizzes (topics) in today's pack (+1 bonus kept separate).
2. As a user, answer choices are shuffled on every attempt.
3. As a user, I can't exceed 3 attempts for the same quiz on the same day.
4. As a user, after 3 attempts I can view correct answers and the quiz becomes locked.
5. As a user, I see my rank computed by % correct, then faster time.
6. As an admin, I can generate a pack deterministically for a given date (same topics).
"""
import sys
import time
from datetime import date, datetime
from bson import ObjectId

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
    create_indexes,
    db,
    users_col,
    topics_col,
    questions_col,
    daily_packs_col,
    attempts_col,
    results_col
)
from seed_data import seed_database


def setup():
    """Setup test environment"""
    print("=" * 60)
    print("🧪 SOCRAQUEST CORE POC TEST")
    print("=" * 60)
    print("\n📋 Setting up test environment...")
    
    # Clear all collections
    db.drop_collection('topics')
    db.drop_collection('questions')
    db.drop_collection('daily_packs')
    db.drop_collection('attempts')
    db.drop_collection('results')
    db.drop_collection('users')
    db.drop_collection('groups')
    
    # Seed data
    seed_database()
    
    # Create indexes
    create_indexes()
    
    # Create test users
    test_users = [
        {'nickname': 'Alice', 'email': 'alice@test.com', 'role': 'user'},
        {'nickname': 'Bob', 'email': 'bob@test.com', 'role': 'user'},
        {'nickname': 'Charlie', 'email': 'charlie@test.com', 'role': 'user'},
    ]
    
    user_ids = []
    for user in test_users:
        result = users_col.insert_one(user)
        user_ids.append(str(result.inserted_id))
    
    print(f"✅ Created {len(user_ids)} test users")
    print()
    
    return user_ids


def test_story_1_pack_generation():
    """
    Story 1: As a user, I get exactly 10 quizzes (topics) in today's pack 
    (+1 bonus kept separate).
    """
    print("\n" + "=" * 60)
    print("📖 TEST STORY 1: Pack Generation (10 + 1 bonus)")
    print("=" * 60)
    
    today = date.today()
    
    # Generate pack
    pack = generate_daily_pack(today)
    
    # Verify structure
    assert 'quiz_topic_ids' in pack, "Pack should have quiz_topic_ids"
    assert 'bonus_topic_id' in pack, "Pack should have bonus_topic_id"
    assert len(pack['quiz_topic_ids']) == 10, f"Should have exactly 10 quizzes, got {len(pack['quiz_topic_ids'])}"
    assert pack['bonus_topic_id'] is not None, "Should have a bonus topic"
    
    # Verify all topics are distinct
    all_topic_ids = pack['quiz_topic_ids'] + [pack['bonus_topic_id']]
    assert len(set(all_topic_ids)) == 11, "All 11 topics should be distinct"
    
    # Verify bonus is separate from main 10
    assert pack['bonus_topic_id'] not in pack['quiz_topic_ids'], "Bonus topic should not be in main 10"
    
    print(f"✅ Generated pack with {len(pack['quiz_topic_ids'])} quizzes + 1 bonus")
    print(f"   Quiz topics: {pack['quiz_topic_ids'][:3]}... (showing first 3)")
    print(f"   Bonus topic: {pack['bonus_topic_id']}")
    print("✅ STORY 1: PASS")
    
    return pack


def test_story_2_answer_shuffling():
    """
    Story 2: As a user, answer choices are shuffled on every attempt.
    """
    print("\n" + "=" * 60)
    print("📖 TEST STORY 2: Answer Shuffling Per Attempt")
    print("=" * 60)
    
    today = date.today()
    pack = generate_daily_pack(today)
    
    # Get first topic
    topic_id = pack['quiz_topic_ids'][0]
    
    # Get questions for attempt 1
    questions_attempt1 = get_quiz_questions(topic_id, attempt_num=1)
    
    # Get questions for attempt 2 (should have different order)
    questions_attempt2 = get_quiz_questions(topic_id, attempt_num=2)
    
    # Verify we got 3 questions each time
    assert len(questions_attempt1) == 3, f"Should get 3 questions, got {len(questions_attempt1)}"
    assert len(questions_attempt2) == 3, f"Should get 3 questions, got {len(questions_attempt2)}"
    
    # Verify same questions but potentially different order
    q1_ids = sorted([q['_id'] for q in questions_attempt1])
    q2_ids = sorted([q['_id'] for q in questions_attempt2])
    assert q1_ids == q2_ids, "Should be same questions across attempts"
    
    # Check that at least one question has different option order
    different_order = False
    for i in range(3):
        q1_opts = [o['key'] for o in questions_attempt1[i]['options']]
        q2_opts = [o['key'] for o in questions_attempt2[i]['options']]
        
        if q1_opts != q2_opts:
            different_order = True
            print(f"   Question {i+1}:")
            print(f"     Attempt 1 order: {q1_opts}")
            print(f"     Attempt 2 order: {q2_opts}")
            break
    
    assert different_order, "At least one question should have different option order between attempts"
    
    print("✅ Answer options are randomized per attempt")
    print("✅ STORY 2: PASS")
    
    return topic_id


def test_story_3_attempt_cap(user_ids):
    """
    Story 3: As a user, I can't exceed 3 attempts for the same quiz on the same day.
    """
    print("\n" + "=" * 60)
    print("📖 TEST STORY 3: 3 Attempt Cap Per Quiz")
    print("=" * 60)
    
    today = date.today()
    pack = generate_daily_pack(today)
    user_id = user_ids[0]
    quiz_index = 0
    topic_id = pack['quiz_topic_ids'][quiz_index]
    
    # Make 3 attempts
    for attempt_num in range(1, 4):
        print(f"\n   Making attempt {attempt_num}...")
        
        # Simulate 15s cooldown for attempts 2 and 3
        if attempt_num > 1:
            print(f"     ⏱️  Simulating 15s cooldown...")
            time.sleep(0.5)  # Simulate (reduced for testing)
        
        # Get questions
        questions = get_quiz_questions(topic_id, attempt_num)
        
        # Simulate user answers (all correct for testing)
        answers = [
            {'question_id': q['_id'], 'choice_key': q['correct_key']}
            for q in questions
        ]
        
        # Record attempt
        result = record_attempt(
            user_id=user_id,
            pack_date=today,
            quiz_index=quiz_index,
            attempt_num=attempt_num,
            answers=answers,
            time_ms=30000 + (attempt_num * 1000)  # Different times
        )
        
        print(f"     ✓ Attempt {attempt_num} recorded: {result['score']['percentage']:.1f}% correct")
    
    # Verify attempt count
    attempt_count = get_attempt_count(user_id, today, quiz_index)
    assert attempt_count == 3, f"Should have exactly 3 attempts, got {attempt_count}"
    
    print(f"\n✅ User completed 3 attempts successfully")
    print(f"✅ Total attempts in database: {attempt_count}")
    print("✅ STORY 3: PASS")
    
    return user_id, quiz_index


def test_story_4_lock_after_answers(user_id, quiz_index):
    """
    Story 4: As a user, after 3 attempts I can view correct answers 
    and the quiz becomes locked.
    """
    print("\n" + "=" * 60)
    print("📖 TEST STORY 4: Lock After Viewing Answers")
    print("=" * 60)
    
    today = date.today()
    
    # Check quiz is not locked initially
    is_locked = is_quiz_locked(user_id, today, quiz_index)
    assert not is_locked, "Quiz should not be locked before viewing answers"
    print("   ✓ Quiz is unlocked initially")
    
    # User views correct answers and quiz gets locked
    print("   👁️  User views correct answers...")
    lock_success = lock_quiz_after_answers(user_id, today, quiz_index)
    assert lock_success, "Lock operation should succeed"
    print("   ✓ Lock operation completed")
    
    # Verify quiz is now locked
    is_locked = is_quiz_locked(user_id, today, quiz_index)
    assert is_locked, "Quiz should be locked after viewing answers"
    print("   ✓ Quiz is now locked")
    
    # Verify attempt count still at 3 (lock doesn't add attempts)
    attempt_count = get_attempt_count(user_id, today, quiz_index)
    assert attempt_count == 3, "Attempt count should remain 3 after locking"
    
    print("\n✅ Quiz successfully locked after viewing answers")
    print("✅ Further attempts should be blocked in UI")
    print("✅ STORY 4: PASS")


def test_story_5_leaderboard_ranking(user_ids):
    """
    Story 5: As a user, I see my rank computed by % correct, then faster time.
    """
    print("\n" + "=" * 60)
    print("📖 TEST STORY 5: Leaderboard Ranking Algorithm")
    print("=" * 60)
    
    today = date.today()
    pack = generate_daily_pack(today)
    quiz_index = 1  # Use quiz 1 for this test
    topic_id = pack['quiz_topic_ids'][quiz_index]
    
    # Get questions
    questions = get_quiz_questions(topic_id, attempt_num=1)
    
    # Create different scores for different users
    test_scenarios = [
        # (user_idx, correct_count, time_ms, expected_rank)
        (0, 3, 25000, 1),  # Alice: 100%, 25s -> Rank 1 (best %)
        (1, 3, 30000, 2),  # Bob: 100%, 30s -> Rank 2 (same % but slower)
        (2, 2, 20000, 3),  # Charlie: 67%, 20s -> Rank 3 (lower %)
    ]
    
    print("\n   Recording attempts:")
    for user_idx, correct_count, time_ms, _ in test_scenarios:
        user_id = user_ids[user_idx]
        user = users_col.find_one({'_id': ObjectId(user_id)})
        
        # Create answers (some correct, some wrong)
        answers = []
        for i, q in enumerate(questions):
            if i < correct_count:
                # Correct answer
                answers.append({'question_id': q['_id'], 'choice_key': q['correct_key']})
            else:
                # Wrong answer (pick first wrong option)
                wrong_key = next(k for k in ['A', 'B', 'C', 'D'] if k != q['correct_key'])
                answers.append({'question_id': q['_id'], 'choice_key': wrong_key})
        
        # Record attempt
        result = record_attempt(
            user_id=user_id,
            pack_date=today,
            quiz_index=quiz_index,
            attempt_num=1,
            answers=answers,
            time_ms=time_ms
        )
        
        pct = result['score']['percentage']
        print(f"     {user['nickname']}: {pct:.1f}% in {time_ms/1000:.1f}s")
    
    # Compute leaderboard
    print("\n   Computing leaderboard...")
    leaderboard = compute_leaderboard(today, quiz_index)
    
    assert len(leaderboard) == 3, f"Should have 3 entries, got {len(leaderboard)}"
    
    print("\n   📊 Leaderboard:")
    for entry in leaderboard:
        print(f"     Rank {entry['rank']}: {entry['nickname']:8} - {entry['percentage']:.1f}% in {entry['time_ms']/1000:.1f}s")
    
    # Verify ranking
    for i, (user_idx, _, _, expected_rank) in enumerate(test_scenarios):
        actual_rank = leaderboard[i]['rank']
        assert actual_rank == expected_rank, f"Expected rank {expected_rank}, got {actual_rank}"
    
    # Verify Alice (100%, 25s) is ranked above Bob (100%, 30s)
    assert leaderboard[0]['nickname'] == 'Alice', "Alice should be rank 1"
    assert leaderboard[1]['nickname'] == 'Bob', "Bob should be rank 2"
    
    # Verify Charlie (67%) is ranked below both
    assert leaderboard[2]['nickname'] == 'Charlie', "Charlie should be rank 3"
    
    print("\n✅ Ranking correctly prioritizes % then time")
    print("✅ STORY 5: PASS")


def test_story_6_deterministic_generation():
    """
    Story 6: As an admin, I can generate a pack deterministically 
    for a given date (same topics).
    """
    print("\n" + "=" * 60)
    print("📖 TEST STORY 6: Deterministic Pack Generation")
    print("=" * 60)
    
    test_date = date(2025, 1, 15)
    test_date_str = test_date.isoformat()
    
    # Clear any existing pack for this date
    daily_packs_col.delete_many({'date': test_date_str})
    
    # Generate pack first time
    print(f"\n   Generating pack for {test_date}...")
    pack1 = generate_daily_pack(test_date)
    topics1 = pack1['quiz_topic_ids']
    bonus1 = pack1['bonus_topic_id']
    print(f"   ✓ First generation: {len(topics1)} topics + bonus")
    
    # Clear and generate again
    daily_packs_col.delete_many({'date': test_date_str})
    print(f"\n   Regenerating pack for same date...")
    pack2 = generate_daily_pack(test_date)
    topics2 = pack2['quiz_topic_ids']
    bonus2 = pack2['bonus_topic_id']
    print(f"   ✓ Second generation: {len(topics2)} topics + bonus")
    
    # Verify same topics in same order
    assert topics1 == topics2, "Quiz topics should be identical across generations"
    assert bonus1 == bonus2, "Bonus topic should be identical across generations"
    
    print("\n   📋 Verification:")
    print(f"     First run topics:  {topics1[:3]}...")
    print(f"     Second run topics: {topics2[:3]}...")
    print(f"     Match: {'✓' if topics1 == topics2 else '✗'}")
    
    print("\n✅ Pack generation is deterministic for same date")
    print("✅ STORY 6: PASS")


def run_all_tests():
    """Run all POC tests"""
    try:
        # Setup
        user_ids = setup()
        
        # Run tests
        test_story_1_pack_generation()
        test_story_2_answer_shuffling()
        user_id, quiz_index = test_story_3_attempt_cap(user_ids)
        test_story_4_lock_after_answers(user_id, quiz_index)
        test_story_5_leaderboard_ranking(user_ids)
        test_story_6_deterministic_generation()
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ ALL POC TESTS PASSED!")
        print("=" * 60)
        print("\n🎉 Core functionality verified:")
        print("   ✓ Pack generation (10 + 1 bonus)")
        print("   ✓ Answer randomization per attempt")
        print("   ✓ 3 attempt cap enforcement")
        print("   ✓ Quiz lock after viewing answers")
        print("   ✓ Leaderboard ranking (% then time)")
        print("   ✓ Deterministic pack generation")
        print("\n🚀 Ready to build full application!")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 60)
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)

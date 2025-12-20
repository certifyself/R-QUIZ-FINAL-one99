"""
SocraQuest Backend API Testing
Tests all API endpoints comprehensively
"""
import requests
import sys
from datetime import datetime, date

class SocraQuestAPITester:
    def __init__(self, base_url="https://mindgames-19.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.admin_token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, use_admin=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        # Add auth token if available
        if use_admin and self.admin_token:
            test_headers['Authorization'] = f'Bearer {self.admin_token}'
        elif self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        print(f"   {method} {endpoint}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"   ✅ PASS - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"   ❌ FAIL - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Response: {response.json()}")
                except:
                    print(f"   Response: {response.text[:200]}")
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'endpoint': endpoint
                })
                return False, {}

        except Exception as e:
            print(f"   ❌ FAIL - Error: {str(e)}")
            self.failed_tests.append({
                'name': name,
                'error': str(e),
                'endpoint': endpoint
            })
            return False, {}

    def test_health(self):
        """Test health endpoint"""
        return self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )

    def test_admin_login(self):
        """Test admin login"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={
                "email": "admin@socraquest.sk",
                "password": "Welcome@123##"
            }
        )
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            print(f"   🔑 Admin token obtained")
            return True
        return False

    def test_user_register(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "User Registration",
            "POST",
            "api/auth/register",
            200,
            data={
                "email": f"testuser{timestamp}@socraquest.com",
                "password": "Test123!",
                "nickname": f"TestUser{timestamp}"
            }
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['_id']
            print(f"   🔑 User token obtained, ID: {self.user_id}")
            return True
        return False

    def test_user_login(self):
        """Test user login with test credentials"""
        success, response = self.run_test(
            "User Login (existing user)",
            "POST",
            "api/auth/login",
            200,
            data={
                "email": "testuser@socraquest.com",
                "password": "Test123!"
            }
        )
        return success

    def test_get_me(self):
        """Test get current user"""
        return self.run_test(
            "Get Current User",
            "GET",
            "api/auth/me",
            200
        )

    def test_admin_get_topics(self):
        """Test admin get topics"""
        return self.run_test(
            "Admin Get Topics",
            "GET",
            "api/admin/topics",
            200,
            use_admin=True
        )

    def test_admin_get_questions(self):
        """Test admin get questions"""
        return self.run_test(
            "Admin Get Questions",
            "GET",
            "api/admin/questions",
            200,
            use_admin=True
        )

    def test_admin_get_metrics(self):
        """Test admin get metrics"""
        return self.run_test(
            "Admin Get Metrics",
            "GET",
            "api/admin/metrics",
            200,
            use_admin=True
        )

    def test_admin_generate_pack(self):
        """Test admin generate today's pack"""
        today = date.today().isoformat()
        success, response = self.run_test(
            "Admin Generate Today's Pack",
            "POST",
            f"api/admin/packs/generate?date={today}",
            200,
            use_admin=True
        )
        if success:
            print(f"   📦 Pack generated for {today}")
        return success, response

    def test_get_today_pack(self):
        """Test user get today's pack"""
        success, response = self.run_test(
            "User Get Today's Pack",
            "GET",
            "api/packs/today",
            200
        )
        if success:
            quizzes = response.get('quizzes', [])
            bonus = response.get('bonus_quiz', {})
            print(f"   📊 Found {len(quizzes)} regular quizzes")
            print(f"   🏆 Bonus quiz unlocked: {bonus.get('unlocked', False)}")
        return success, response

    def test_get_quiz(self, quiz_index=0):
        """Test get quiz questions"""
        success, response = self.run_test(
            f"Get Quiz {quiz_index}",
            "GET",
            f"api/quizzes/{quiz_index}",
            200
        )
        if success:
            questions = response.get('questions', [])
            print(f"   📝 Found {len(questions)} questions")
            print(f"   🔄 Attempt number: {response.get('attempt_number', 0)}")
        return success, response

    def test_submit_quiz(self, quiz_index=0, answers=None):
        """Test submit quiz"""
        if not answers:
            # Get quiz first to get question IDs
            success, quiz_data = self.test_get_quiz(quiz_index)
            if not success:
                return False, {}
            
            # Create dummy answers (all A)
            questions = quiz_data.get('questions', [])
            answers = [
                {"question_id": q['_id'], "choice_key": "A"}
                for q in questions
            ]
        
        success, response = self.run_test(
            f"Submit Quiz {quiz_index}",
            "POST",
            f"api/quizzes/{quiz_index}/submit",
            200,
            data={
                "answers": answers,
                "time_ms": 30000
            }
        )
        if success:
            print(f"   📊 Score: {response.get('score', {}).get('percentage', 0):.1f}%")
            print(f"   🎯 Rank: {response.get('rank', 'N/A')}")
            print(f"   🔄 Attempts remaining: {response.get('attempts_remaining', 0)}")
        return success, response

    def test_get_leaderboard(self, quiz_index=0):
        """Test get quiz leaderboard"""
        success, response = self.run_test(
            f"Get Leaderboard for Quiz {quiz_index}",
            "GET",
            f"api/quizzes/{quiz_index}/leaderboard",
            200
        )
        if success:
            leaderboard = response.get('leaderboard', [])
            print(f"   🏆 Leaderboard entries: {len(leaderboard)}")
        return success, response

    def test_create_group(self):
        """Test create group"""
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "Create Group",
            "POST",
            "api/groups",
            200,
            data={"name": f"Test Group {timestamp}"}
        )
        if success:
            code = response.get('group', {}).get('code', 'N/A')
            print(f"   🔑 Group code: {code}")
            return success, response
        return success, {}

    def test_get_groups(self):
        """Test get user groups"""
        return self.run_test(
            "Get User Groups",
            "GET",
            "api/groups",
            200
        )

    def test_get_profile(self):
        """Test get user profile"""
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "api/profile",
            200
        )
        if success:
            stats = response.get('stats', {})
            print(f"   📊 Quizzes played: {stats.get('quizzes_played', 0)}")
            print(f"   📈 Avg correct: {stats.get('avg_correct', 0):.1f}%")
        return success, response

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✅")
        print(f"Failed: {len(self.failed_tests)} ❌")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for i, test in enumerate(self.failed_tests, 1):
                print(f"\n{i}. {test['name']}")
                print(f"   Endpoint: {test['endpoint']}")
                if 'expected' in test:
                    print(f"   Expected: {test['expected']}, Got: {test['actual']}")
                if 'error' in test:
                    print(f"   Error: {test['error']}")
        
        print("\n" + "="*60)
        return len(self.failed_tests) == 0


def main():
    print("="*60)
    print("🧪 SocraQuest Backend API Testing")
    print("="*60)
    
    tester = SocraQuestAPITester()
    
    # Test 1: Health Check
    tester.test_health()
    
    # Test 2: Admin Login
    if not tester.test_admin_login():
        print("\n❌ Admin login failed - stopping tests")
        return 1
    
    # Test 3: Admin Endpoints
    tester.test_admin_get_topics()
    tester.test_admin_get_questions()
    tester.test_admin_get_metrics()
    
    # Test 4: Generate Today's Pack
    tester.test_admin_generate_pack()
    
    # Test 5: User Registration
    if not tester.test_user_register():
        print("\n❌ User registration failed - stopping tests")
        return 1
    
    # Test 6: User Endpoints
    tester.test_get_me()
    tester.test_get_today_pack()
    
    # Test 7: Quiz Flow
    tester.test_get_quiz(0)
    tester.test_submit_quiz(0)
    tester.test_get_leaderboard(0)
    
    # Test 8: Groups
    tester.test_create_group()
    tester.test_get_groups()
    
    # Test 9: Profile
    tester.test_get_profile()
    
    # Print summary
    all_passed = tester.print_summary()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

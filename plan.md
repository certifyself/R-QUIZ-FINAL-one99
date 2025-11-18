# SocraQuest — Execution Plan (PWA, FastAPI, MongoDB)

## 1) Objectives
- Deliver a mobile-first PWA for daily trivia with admin panel, JWT auth, and MongoDB.
- Core gameplay: daily pack generation (10 + 1 bonus), 30 Q/quiz, 3 attempts with cooldowns, randomized answers, scoring, leaderboards, groups, badges, quiz lock after answers.
- Placeholder Ad hooks: banner (quiz screen), rewarded/interstitial gate for attempt 2 & 3 and quiz switching.
- Build Admin Panel first, seed admin user (admin@socraquest.sk / Welcome@123##), then full user app.

## 2) Architecture Overview
- Frontend: React PWA (mobile-first), routes:
  - / (Home/Today’s Quest), /auth/login, /auth/register, /quiz/:id, /results, /rankings, /groups, /profile
  - /admin (Topics, Questions, Daily Packs, Dashboard)
  - Components include BannerAdPlaceholder and RewardedGate (15s + continue), all interactive elements have data-testid
- Backend: FastAPI, MongoDB (MONGO_URL), JWT auth, REST; all routes under /api
- Data Models (Mongo Collections):
  - users { _id, email, password_hash, nickname, avatar_seed, role, stats, badges:[] }
  - topics { _id, name, active }
  - questions { _id, topic_id, text, options:[{key,label}], correct_key, active }
  - daily_packs { _id, date, quiz_topic_ids:[topic_id x10], bonus_topic_id, generated_at }
  - attempts { _id, user_id, date, quiz_index(0-9), attempt_num(1-3), answers:[{q_id, choice_key}], correct_count, time_ms, finished_at }
  - results { _id, user_id, date, quiz_index, best_pct, best_time_ms, locked_after_answers:boolean }
  - groups { _id, name, code, owner_id, members:[user_id], created_at }
  - badges { _id, code, name, description, active }
- Key Logic Services:
  - generate_daily_pack(date) → 10 topics (distinct) + 1 bonus topic
  - get_quiz_questions(topic_id) → 3 questions with randomized options per attempt
  - record_attempt(user, quiz_index, attempt_num, answers) → compute score/time
  - compute_leaderboard(date, quiz_index[, group_id]) → sort by pct desc, then time asc
  - lock_quiz_after_answers(user, date, quiz_index)

## 3) Phase 1 — Core POC (Isolated)
Goal: Prove the hardest core works before app build: pack generation, attempts (3), cooldown gates, answer randomization, scoring, leaderboards, lock-after-answers.

Scope (Backend + one Python test script, no UI):
1. Minimal schemas in FastAPI service layer (or standalone module) for: topics, questions, daily pack, attempts, results (Mongo).
2. Seed script for: 10+ topics and >=30 questions (3 per topic minimum) with correct answers.
3. Implement pure functions:
   - generate_daily_pack(date)
   - randomize_answers_for_attempt(qs, seed or shuffle)
   - score_attempt(answers, ground_truth)
   - upsert_best_result(user, quiz_index, pct, time_ms)
   - compute_leaderboard(date, quiz_index[, group])
   - lock_quiz_after_answers()
4. Single Python test file test_core.py that:
   - Seeds topics/questions
   - Generates today’s pack and validates 10 distinct topics + 1 bonus
   - Simulates a user taking quiz 1 three times with randomized options and 15s gates (simulated wait)
   - Validates attempt cap, no answer reveal until 3rd attempt done
   - After 3rd attempt: reveal answers → lock quiz → further attempts blocked
   - Inserts attempts for multiple users → validates leaderboard ordering by pct desc, time asc
5. Web search (brief) during POC: confirm Mongo compound indexes for leaderboards (date, quiz_index, best_pct desc, best_time_ms asc), and best practice for random option order and idempotent pack generation.
6. Success Criteria:
   - test_core.py prints PASS for all user stories below and exits 0.

POC User Stories (≥5):
1. As a user, I get exactly 10 quizzes (topics) in today’s pack (+1 bonus kept separate).
2. As a user, answer choices are shuffled on every attempt.
3. As a user, I can’t exceed 3 attempts for the same quiz on the same day.
4. As a user, after 3 attempts I can view correct answers and the quiz becomes locked.
5. As a user, I see my rank computed by % correct, then faster time.
6. As an admin, I can generate a pack deterministically for a given date (same topics).

## 4) Phase 2 — Full App Development
Backend (FastAPI, /api):
- Auth: POST /api/auth/register, /api/auth/login, GET /api/auth/me (JWT)
- Admin (role=admin):
  - Topics: GET/POST/PUT/PATCH /api/admin/topics
  - Questions: GET/POST/PUT/PATCH /api/admin/questions (filter by topic)
  - Daily Packs: GET /api/admin/packs?date=YYYY-MM-DD, POST /api/admin/packs/generate
  - Dashboard: GET /api/admin/metrics (users, quizzes played today, avg success)
- Daily Pack (user):
  - GET /api/packs/today → topics (10) + bonus meta
  - GET /api/quizzes/:index → returns 3 questions with randomized options (per attempt)
  - POST /api/quizzes/:index/submit → body: answers, time_ms; server computes correctness, saves attempt, upserts best result
  - POST /api/quizzes/:index/lock-after-answers → locks quiz for user
  - GET /api/quizzes/:index/leaderboard[?group_id]
- Groups:
  - POST /api/groups (name) → code
  - POST /api/groups/join (code)
  - GET /api/groups → user groups
  - GET /api/groups/:id/members, GET /api/groups/:id/leaderboard
- Profile/Badges:
  - GET /api/profile, GET /api/badges, POST /api/profile/avatar, computed stats endpoints
- Data/Indexes:
  - Ensure compound indexes: results(date, quiz_index, best_pct desc, best_time_ms asc), attempts(user_id,date,quiz_index,attempt_num), daily_packs(date unique)
- Serialization helpers for ObjectId/datetime.

Frontend (React PWA):
- PWA Setup: manifest.json, service worker, mobile-first layout, install prompt.
- Auth pages, Home/Today’s Quest (progress across 10 quizzes + bonus lock), Quiz screen:
  - Timer, question index, randomized options, banner Ad placeholder fixed bottom
  - Before attempt 2 & 3 and on quiz switches: RewardedGate (15s + Continue) simulating interstitial
  - Results screen: accuracy %, total time, rank, CTA: Try Improve (if attempts left) or View Correct Answers (after 3rd → then Lock)
- Rankings: Global and Group tabs; current user highlighted
- Groups: My Groups, Create group (shows code), Join by code, Group detail ranking for today
- Profile: nickname/avatar, stats (played, avg %, best), badges list (text-only MVP)
- Admin Panel (/admin):
  - Auth gated by role, Sidebar: Topics, Questions, Daily Packs, Dashboard
  - Topics CRUD, Questions CRUD (4 options + correct), Generate Pack (by date), View Pack contents
- Ads Placeholders:
  - <BannerAdPlaceholder data-testid="banner-ad" />
  - <RewardedGate data-testid="rewarded-gate" seconds=15 onFinish=.../>
- Styling: dark blue/teal theme, Socrates silhouette in header; call design_agent for detailed guidelines and tokens.

Phase 2 User Stories (≥8):
1. As an admin, I can create topics and add active/inactive questions with marked correct option.
2. As an admin, I can generate today’s pack and preview which questions are inside each quiz.
3. As a user, I can register/login and see today’s 10 quizzes and bonus locked until all done.
4. As a user, I answer 30 questions, see a non-intrusive banner, and get a results screen with rank.
5. As a user, I can retry with a 15s interstitial gate for attempts 2 and 3.
6. As a user, after 3 attempts I can view answers and the quiz becomes locked.
7. As a user, I can join a group via code and see my group’s leaderboard for today.
8. As a user, my rank highlights me in both global and group boards.
9. As a user, I see the bonus quiz unlock only after all 10 standard quizzes are completed.
10. As a user, I can resume today’s progress and see attempts remaining per quiz.

Testing (Phase 2):
- Use testing_agent_v3 for E2E: auth flows, admin CRUD, pack generation, quiz flow (attempt caps, cooldowns), lock-after-answers, leaderboards, groups join/code, banner & rewarded placeholders presence.
- Skip camera/drag-drop. Provide seeded admin credentials.

## 5) Implementation Steps (Condensed)
1. Phase 1 POC
   - Create core models/services in backend; seed script
   - Implement core functions (generate pack, randomize, score, upsert best, leaderboard, lock)
   - Write test_core.py covering POC stories; add Mongo indexes
   - Run POC, fix until PASS
2. Phase 2 App
   - Backend REST endpoints (/api prefix), JWT auth, role-based admin
   - Frontend PWA scaffolding, routes, pages, components; Ad placeholders
   - Integrate API on all pages; state for attempts/progress; error/loading UX
   - Design pass using design_agent; implement theme
   - E2E test with testing_agent_v3; fix; retest

## 6) Next Actions
- Implement Phase 1 POC immediately (core services + test_core.py) and validate.
- After POC PASS, I’ll take ~20–30 minutes to build the full app UI + backend endpoints and run E2E tests.

## 7) Success Criteria
- POC: test_core.py passes all core stories; deterministic daily pack; correct leaderboard sort; lock-after-answers enforced.
- App: Admin CRUD works; Today’s Quest flows work end-to-end with attempts, cooldowns, randomized answers, ranking, groups, and lock-after-answers; bonus unlock rule enforced.
- Ads: Banner and rewarded placeholders consistently shown where specified.
- Quality: All API routes under /api, no hardcoded env; consistent serialization; mobile-first UI; clear errors; all key components with data-testid.

---
Phase 1: POC required and prioritized. Phase 2: All user stories covered in Development and testing. Phase 2: End to End Testing using Testing Agent.

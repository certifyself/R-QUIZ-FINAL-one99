# SocraQuest - Local Development Setup Guide

## 📋 Technical Specifications

### Tech Stack
| Component | Technology | Version |
|-----------|------------|---------|
| **Frontend** | React | 18.x |
| **Backend** | FastAPI (Python) | 0.100+ |
| **Database** | MongoDB | 6.0+ |
| **Styling** | TailwindCSS + shadcn/ui | 3.x |
| **Authentication** | JWT (JSON Web Tokens) | - |
| **Internationalization** | i18next | 23.x |

### System Requirements
- **Node.js**: v18.x or higher
- **Python**: 3.10 or higher
- **MongoDB**: 6.0+ (local or cloud - MongoDB Atlas)
- **Package Managers**: npm/yarn (frontend), pip (backend)
- **OS**: Windows, macOS, or Linux

---

## 🚀 Step-by-Step Setup

### 1. Clone/Download the Project

```bash
# Create project directory
mkdir socraquest
cd socraquest

# Copy the backend and frontend folders to this directory
# You should have:
# - /backend
# - /frontend
```

### 2. Setup MongoDB

#### Option A: Local MongoDB
```bash
# Install MongoDB Community Edition
# macOS (with Homebrew):
brew tap mongodb/brew
brew install mongodb-community@6.0
brew services start mongodb-community@6.0

# Ubuntu/Debian:
sudo apt-get install -y mongodb-org
sudo systemctl start mongod

# Windows: Download from https://www.mongodb.com/try/download/community
```

#### Option B: MongoDB Atlas (Cloud - Recommended for beginners)
1. Go to https://www.mongodb.com/atlas
2. Create a free account
3. Create a new cluster (free tier)
4. Get your connection string: `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/socraquest`

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Or create manually (see Environment Variables section below)
```

### 4. Setup Frontend

```bash
cd frontend

# Install dependencies
yarn install
# OR
npm install

# Create .env file
cp .env.example .env
# Or create manually (see Environment Variables section below)
```

---

## 🔧 Environment Variables

### Backend (.env)
Create `/backend/.env`:

```env
# MongoDB Connection
MONGO_URL=mongodb://localhost:27017/socraquest
# OR for MongoDB Atlas:
# MONGO_URL=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/socraquest

# JWT Secret (generate a random string)
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# Optional: Firebase (for push notifications)
# FIREBASE_CREDENTIALS_JSON={"type":"service_account",...}
```

### Frontend (.env)
Create `/frontend/.env`:

```env
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## ▶️ Running the Application

### Terminal 1: Start Backend
```bash
cd backend
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Run the server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```
Backend will be available at: `http://localhost:8001`

### Terminal 2: Start Frontend
```bash
cd frontend

# Run development server
yarn start
# OR
npm start
```
Frontend will be available at: `http://localhost:3000`

---

## 👤 Create Admin User

After starting the application, create an admin user:

```bash
# Using curl (run this after backend is started)
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@socraquest.local",
    "password": "YourSecurePassword123",
    "nickname": "Admin"
  }'
```

Then, manually set the user as admin in MongoDB:

```bash
# Connect to MongoDB
mongosh socraquest

# Update user role to admin
db.users.updateOne(
  { email: "admin@socraquest.local" },
  { $set: { role: "admin" } }
)
```

---

## 📁 Project Structure

```
socraquest/
├── backend/
│   ├── server.py           # Main FastAPI application
│   ├── core_services.py    # Quiz generation, scoring logic
│   ├── badge_service.py    # Badge system
│   ├── push_service.py     # Push notifications (optional)
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React app with routes
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   │   ├── user/      # User-facing pages
│   │   │   └── admin/     # Admin panel pages
│   │   ├── contexts/      # React contexts (Auth)
│   │   ├── lib/           # API client, utilities
│   │   ├── locales/       # Translations (en.json, sk.json)
│   │   └── i18n.js        # i18next configuration
│   ├── package.json       # Node.js dependencies
│   └── .env              # Environment variables
│
└── uploads/              # Uploaded images (created automatically)
```

---

## 📦 Required Python Packages

```txt
# requirements.txt
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pymongo>=4.5.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
pandas>=2.0.0
openpyxl>=3.1.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

---

## 📦 Required Node.js Packages

Key dependencies in `package.json`:

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.x",
    "axios": "^1.x",
    "i18next": "^23.x",
    "react-i18next": "^13.x",
    "tailwindcss": "^3.x",
    "framer-motion": "^10.x",
    "lucide-react": "^0.x",
    "sonner": "^1.x",
    "@radix-ui/react-dialog": "^1.x",
    "@radix-ui/react-select": "^1.x"
  }
}
```

---

## 🔗 API Endpoints Overview

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### User APIs
- `GET /api/packs/today` - Get today's quiz pack
- `GET /api/quizzes/{index}` - Get quiz questions
- `POST /api/quizzes/{index}/submit` - Submit quiz answers
- `GET /api/quizzes/{index}/answers` - Get correct answers
- `GET /api/profile` - Get user profile
- `GET /api/rankings/daily` - Get daily leaderboard

### Admin APIs
- `GET /api/admin/topics` - List all topics
- `POST /api/admin/topics` - Create topic
- `GET /api/admin/questions` - List questions
- `POST /api/admin/questions` - Create question
- `POST /api/admin/upload-image` - Upload image
- `POST /api/admin/packs/generate` - Generate daily pack

---

## 🐛 Troubleshooting

### MongoDB Connection Error
```
Error: MongoClient connection failed
```
- Check if MongoDB is running: `mongosh --eval "db.version()"`
- Verify MONGO_URL in `.env` is correct

### CORS Error in Browser
```
Access-Control-Allow-Origin error
```
- Ensure backend CORS is configured (already set in server.py)
- Check that frontend is using correct `REACT_APP_BACKEND_URL`

### Module Not Found (Python)
```
ModuleNotFoundError: No module named 'xyz'
```
- Activate virtual environment: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

### Port Already in Use
```
Error: Address already in use :8001
```
- Kill existing process: `lsof -i :8001` then `kill -9 <PID>`
- Or use different port: `uvicorn server:app --port 8002`

---

## 🌐 Production Deployment

For production deployment, consider:

1. **Frontend**: Build static files with `yarn build`, deploy to Vercel/Netlify
2. **Backend**: Deploy to Railway, Render, or AWS
3. **Database**: Use MongoDB Atlas (cloud)
4. **Environment**: Set `NODE_ENV=production` and use secure JWT secrets

---

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review server logs for error details
- Ensure all environment variables are correctly set

---

Happy quizzing! 🎯

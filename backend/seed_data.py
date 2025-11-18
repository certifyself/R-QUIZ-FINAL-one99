"""
Seed database with sample topics and questions for SocraQuest POC
"""
import os
from pymongo import MongoClient
from bson import ObjectId

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client['socraquest']

topics_col = db['topics']
questions_col = db['questions']


def seed_database():
    """Seed topics and questions"""
    print("🌱 Seeding database...")
    
    # Clear existing data
    topics_col.delete_many({})
    questions_col.delete_many({})
    
    # Sample topics
    topics_data = [
        "History",
        "Geography",
        "Science",
        "Literature",
        "Mathematics",
        "Art",
        "Music",
        "Sports",
        "Technology",
        "Cinema",
        "Philosophy",
        "Politics"
    ]
    
    topic_ids = []
    for topic_name in topics_data:
        result = topics_col.insert_one({
            'name': topic_name,
            'active': True
        })
        topic_ids.append(result.inserted_id)
        print(f"  ✓ Created topic: {topic_name}")
    
    # Questions for each topic (3 per topic minimum)
    questions_data = {
        "History": [
            {
                "text": "In which year did World War II end?",
                "options": [
                    {"key": "A", "label": "1943"},
                    {"key": "B", "label": "1945"},
                    {"key": "C", "label": "1947"},
                    {"key": "D", "label": "1950"}
                ],
                "correct_key": "B"
            },
            {
                "text": "Who was the first President of the United States?",
                "options": [
                    {"key": "A", "label": "Thomas Jefferson"},
                    {"key": "B", "label": "Benjamin Franklin"},
                    {"key": "C", "label": "George Washington"},
                    {"key": "D", "label": "John Adams"}
                ],
                "correct_key": "C"
            },
            {
                "text": "Which ancient civilization built the pyramids?",
                "options": [
                    {"key": "A", "label": "Greeks"},
                    {"key": "B", "label": "Romans"},
                    {"key": "C", "label": "Egyptians"},
                    {"key": "D", "label": "Babylonians"}
                ],
                "correct_key": "C"
            }
        ],
        "Geography": [
            {
                "text": "What is the capital of France?",
                "options": [
                    {"key": "A", "label": "London"},
                    {"key": "B", "label": "Berlin"},
                    {"key": "C", "label": "Madrid"},
                    {"key": "D", "label": "Paris"}
                ],
                "correct_key": "D"
            },
            {
                "text": "Which is the longest river in the world?",
                "options": [
                    {"key": "A", "label": "Amazon"},
                    {"key": "B", "label": "Nile"},
                    {"key": "C", "label": "Yangtze"},
                    {"key": "D", "label": "Mississippi"}
                ],
                "correct_key": "B"
            },
            {
                "text": "How many continents are there?",
                "options": [
                    {"key": "A", "label": "5"},
                    {"key": "B", "label": "6"},
                    {"key": "C", "label": "7"},
                    {"key": "D", "label": "8"}
                ],
                "correct_key": "C"
            }
        ],
        "Science": [
            {
                "text": "What is the chemical symbol for water?",
                "options": [
                    {"key": "A", "label": "H2O"},
                    {"key": "B", "label": "CO2"},
                    {"key": "C", "label": "O2"},
                    {"key": "D", "label": "N2"}
                ],
                "correct_key": "A"
            },
            {
                "text": "What is the speed of light?",
                "options": [
                    {"key": "A", "label": "300,000 km/s"},
                    {"key": "B", "label": "150,000 km/s"},
                    {"key": "C", "label": "450,000 km/s"},
                    {"key": "D", "label": "600,000 km/s"}
                ],
                "correct_key": "A"
            },
            {
                "text": "Which planet is known as the Red Planet?",
                "options": [
                    {"key": "A", "label": "Venus"},
                    {"key": "B", "label": "Mars"},
                    {"key": "C", "label": "Jupiter"},
                    {"key": "D", "label": "Saturn"}
                ],
                "correct_key": "B"
            }
        ],
        "Literature": [
            {
                "text": "Who wrote 'Romeo and Juliet'?",
                "options": [
                    {"key": "A", "label": "Charles Dickens"},
                    {"key": "B", "label": "William Shakespeare"},
                    {"key": "C", "label": "Jane Austen"},
                    {"key": "D", "label": "Mark Twain"}
                ],
                "correct_key": "B"
            },
            {
                "text": "Which book begins with 'Call me Ishmael'?",
                "options": [
                    {"key": "A", "label": "Moby-Dick"},
                    {"key": "B", "label": "The Great Gatsby"},
                    {"key": "C", "label": "1984"},
                    {"key": "D", "label": "Pride and Prejudice"}
                ],
                "correct_key": "A"
            },
            {
                "text": "Who is the author of Harry Potter series?",
                "options": [
                    {"key": "A", "label": "J.R.R. Tolkien"},
                    {"key": "B", "label": "C.S. Lewis"},
                    {"key": "C", "label": "J.K. Rowling"},
                    {"key": "D", "label": "Roald Dahl"}
                ],
                "correct_key": "C"
            }
        ],
        "Mathematics": [
            {
                "text": "What is 15% of 200?",
                "options": [
                    {"key": "A", "label": "20"},
                    {"key": "B", "label": "30"},
                    {"key": "C", "label": "40"},
                    {"key": "D", "label": "50"}
                ],
                "correct_key": "B"
            },
            {
                "text": "What is the value of π (pi) approximately?",
                "options": [
                    {"key": "A", "label": "2.14"},
                    {"key": "B", "label": "3.14"},
                    {"key": "C", "label": "4.14"},
                    {"key": "D", "label": "5.14"}
                ],
                "correct_key": "B"
            },
            {
                "text": "What is the square root of 144?",
                "options": [
                    {"key": "A", "label": "10"},
                    {"key": "B", "label": "11"},
                    {"key": "C", "label": "12"},
                    {"key": "D", "label": "13"}
                ],
                "correct_key": "C"
            }
        ],
        "Art": [
            {
                "text": "Who painted the Mona Lisa?",
                "options": [
                    {"key": "A", "label": "Michelangelo"},
                    {"key": "B", "label": "Leonardo da Vinci"},
                    {"key": "C", "label": "Raphael"},
                    {"key": "D", "label": "Donatello"}
                ],
                "correct_key": "B"
            },
            {
                "text": "What is the primary color that cannot be made by mixing?",
                "options": [
                    {"key": "A", "label": "Orange"},
                    {"key": "B", "label": "Green"},
                    {"key": "C", "label": "Red"},
                    {"key": "D", "label": "Purple"}
                ],
                "correct_key": "C"
            },
            {
                "text": "Which art movement was Pablo Picasso associated with?",
                "options": [
                    {"key": "A", "label": "Impressionism"},
                    {"key": "B", "label": "Cubism"},
                    {"key": "C", "label": "Surrealism"},
                    {"key": "D", "label": "Expressionism"}
                ],
                "correct_key": "B"
            }
        ],
        "Music": [
            {
                "text": "How many strings does a standard guitar have?",
                "options": [
                    {"key": "A", "label": "4"},
                    {"key": "B", "label": "5"},
                    {"key": "C", "label": "6"},
                    {"key": "D", "label": "7"}
                ],
                "correct_key": "C"
            },
            {
                "text": "Who composed the Four Seasons?",
                "options": [
                    {"key": "A", "label": "Mozart"},
                    {"key": "B", "label": "Beethoven"},
                    {"key": "C", "label": "Vivaldi"},
                    {"key": "D", "label": "Bach"}
                ],
                "correct_key": "C"
            },
            {
                "text": "What does 'forte' mean in music?",
                "options": [
                    {"key": "A", "label": "Soft"},
                    {"key": "B", "label": "Loud"},
                    {"key": "C", "label": "Fast"},
                    {"key": "D", "label": "Slow"}
                ],
                "correct_key": "B"
            }
        ],
        "Sports": [
            {
                "text": "How many players are on a soccer team on the field?",
                "options": [
                    {"key": "A", "label": "9"},
                    {"key": "B", "label": "10"},
                    {"key": "C", "label": "11"},
                    {"key": "D", "label": "12"}
                ],
                "correct_key": "C"
            },
            {
                "text": "In which sport is the term 'love' used?",
                "options": [
                    {"key": "A", "label": "Golf"},
                    {"key": "B", "label": "Tennis"},
                    {"key": "C", "label": "Cricket"},
                    {"key": "D", "label": "Baseball"}
                ],
                "correct_key": "B"
            },
            {
                "text": "How many Olympic rings are there?",
                "options": [
                    {"key": "A", "label": "3"},
                    {"key": "B", "label": "4"},
                    {"key": "C", "label": "5"},
                    {"key": "D", "label": "6"}
                ],
                "correct_key": "C"
            }
        ],
        "Technology": [
            {
                "text": "What does CPU stand for?",
                "options": [
                    {"key": "A", "label": "Central Process Unit"},
                    {"key": "B", "label": "Central Processing Unit"},
                    {"key": "C", "label": "Computer Personal Unit"},
                    {"key": "D", "label": "Central Processor Unit"}
                ],
                "correct_key": "B"
            },
            {
                "text": "Who founded Microsoft?",
                "options": [
                    {"key": "A", "label": "Steve Jobs"},
                    {"key": "B", "label": "Bill Gates"},
                    {"key": "C", "label": "Mark Zuckerberg"},
                    {"key": "D", "label": "Elon Musk"}
                ],
                "correct_key": "B"
            },
            {
                "text": "What does 'HTTP' stand for?",
                "options": [
                    {"key": "A", "label": "HyperText Transfer Protocol"},
                    {"key": "B", "label": "High Transfer Text Protocol"},
                    {"key": "C", "label": "HyperText Technical Protocol"},
                    {"key": "D", "label": "High Tech Transfer Protocol"}
                ],
                "correct_key": "A"
            }
        ],
        "Cinema": [
            {
                "text": "Which movie won the first Academy Award for Best Picture?",
                "options": [
                    {"key": "A", "label": "Wings"},
                    {"key": "B", "label": "The Jazz Singer"},
                    {"key": "C", "label": "Sunrise"},
                    {"key": "D", "label": "Metropolis"}
                ],
                "correct_key": "A"
            },
            {
                "text": "Who directed 'The Godfather'?",
                "options": [
                    {"key": "A", "label": "Martin Scorsese"},
                    {"key": "B", "label": "Francis Ford Coppola"},
                    {"key": "C", "label": "Steven Spielberg"},
                    {"key": "D", "label": "Quentin Tarantino"}
                ],
                "correct_key": "B"
            },
            {
                "text": "In which year was the first 'Star Wars' movie released?",
                "options": [
                    {"key": "A", "label": "1975"},
                    {"key": "B", "label": "1977"},
                    {"key": "C", "label": "1979"},
                    {"key": "D", "label": "1981"}
                ],
                "correct_key": "B"
            }
        ],
        "Philosophy": [
            {
                "text": "Who is known as the father of Western philosophy?",
                "options": [
                    {"key": "A", "label": "Socrates"},
                    {"key": "B", "label": "Plato"},
                    {"key": "C", "label": "Aristotle"},
                    {"key": "D", "label": "Pythagoras"}
                ],
                "correct_key": "A"
            },
            {
                "text": "What is the famous phrase by Descartes?",
                "options": [
                    {"key": "A", "label": "Know thyself"},
                    {"key": "B", "label": "I think, therefore I am"},
                    {"key": "C", "label": "Life is suffering"},
                    {"key": "D", "label": "God is dead"}
                ],
                "correct_key": "B"
            },
            {
                "text": "Who wrote 'The Republic'?",
                "options": [
                    {"key": "A", "label": "Socrates"},
                    {"key": "B", "label": "Plato"},
                    {"key": "C", "label": "Aristotle"},
                    {"key": "D", "label": "Epicurus"}
                ],
                "correct_key": "B"
            }
        ],
        "Politics": [
            {
                "text": "How many members are in the United Nations Security Council?",
                "options": [
                    {"key": "A", "label": "10"},
                    {"key": "B", "label": "12"},
                    {"key": "C", "label": "15"},
                    {"key": "D", "label": "20"}
                ],
                "correct_key": "C"
            },
            {
                "text": "Who was the first female Prime Minister of the United Kingdom?",
                "options": [
                    {"key": "A", "label": "Margaret Thatcher"},
                    {"key": "B", "label": "Theresa May"},
                    {"key": "C", "label": "Angela Merkel"},
                    {"key": "D", "label": "Indira Gandhi"}
                ],
                "correct_key": "A"
            },
            {
                "text": "In which year was the European Union established?",
                "options": [
                    {"key": "A", "label": "1985"},
                    {"key": "B", "label": "1990"},
                    {"key": "C", "label": "1993"},
                    {"key": "D", "label": "2000"}
                ],
                "correct_key": "C"
            }
        ]
    }
    
    # Insert questions
    total_questions = 0
    for topic_name, questions in questions_data.items():
        # Find topic ID
        topic = topics_col.find_one({'name': topic_name})
        if not topic:
            continue
        
        for q_data in questions:
            questions_col.insert_one({
                'topic_id': topic['_id'],
                'text': q_data['text'],
                'options': q_data['options'],
                'correct_key': q_data['correct_key'],
                'active': True
            })
            total_questions += 1
    
    print(f"\n✅ Seeded {len(topics_data)} topics and {total_questions} questions")
    print(f"   Each topic has 3 questions")
    return topic_ids


if __name__ == '__main__':
    seed_database()

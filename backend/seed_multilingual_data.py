"""
Seed database with multilingual sample questions (English + Slovak)
"""
import os
from pymongo import MongoClient
from bson import ObjectId

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client['socraquest']

topics_col = db['topics']
questions_col = db['questions']


def seed_multilingual_database():
    """Seed topics and multilingual questions"""
    print("🌱 Seeding multilingual database...")
    
    # Clear existing data
    topics_col.delete_many({})
    questions_col.delete_many({})
    
    # Sample topics (same in both languages for simplicity)
    topics_data = [
        "History", "Geography", "Science", "Literature", 
        "Mathematics", "Art", "Music", "Sports",
        "Technology", "Cinema", "Philosophy", "Politics"
    ]
    
    topic_ids = {}
    for topic_name in topics_data:
        result = topics_col.insert_one({
            'name': topic_name,
            'active': True
        })
        topic_ids[topic_name] = result.inserted_id
        print(f"  ✓ Created topic: {topic_name}")
    
    # Multilingual questions
    multilingual_questions = {
        "History": [
            {
                "text": {
                    "en": "In which year did World War II end?",
                    "sk": "V ktorom roku skončila druhá svetová vojna?"
                },
                "options": [
                    {"key": "A", "label": {"en": "1943", "sk": "1943"}},
                    {"key": "B", "label": {"en": "1945", "sk": "1945"}},
                    {"key": "C", "label": {"en": "1947", "sk": "1947"}},
                    {"key": "D", "label": {"en": "1950", "sk": "1950"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {
                    "en": "Who was the first President of the United States?",
                    "sk": "Kto bol prvým prezidentom Spojených štátov?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Thomas Jefferson", "sk": "Thomas Jefferson"}},
                    {"key": "B", "label": {"en": "Benjamin Franklin", "sk": "Benjamin Franklin"}},
                    {"key": "C", "label": {"en": "George Washington", "sk": "George Washington"}},
                    {"key": "D", "label": {"en": "John Adams", "sk": "John Adams"}}
                ],
                "correct_key": "C"
            },
            {
                "text": {
                    "en": "Which ancient civilization built the pyramids?",
                    "sk": "Ktorá staroveká civilizácia postavila pyramídy?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Greeks", "sk": "Gréci"}},
                    {"key": "B", "label": {"en": "Romans", "sk": "Rimania"}},
                    {"key": "C", "label": {"en": "Egyptians", "sk": "Egypťania"}},
                    {"key": "D", "label": {"en": "Babylonians", "sk": "Babylončania"}}
                ],
                "correct_key": "C"
            }
        ],
        "Geography": [
            {
                "text": {
                    "en": "What is the capital of France?",
                    "sk": "Aké je hlavné mesto Francúzska?"
                },
                "options": [
                    {"key": "A", "label": {"en": "London", "sk": "Londýn"}},
                    {"key": "B", "label": {"en": "Berlin", "sk": "Berlín"}},
                    {"key": "C", "label": {"en": "Madrid", "sk": "Madrid"}},
                    {"key": "D", "label": {"en": "Paris", "sk": "Paríž"}}
                ],
                "correct_key": "D"
            },
            {
                "text": {
                    "en": "Which is the longest river in the world?",
                    "sk": "Ktorá je najdlhšia rieka na svete?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Amazon", "sk": "Amazonka"}},
                    {"key": "B", "label": {"en": "Nile", "sk": "Níl"}},
                    {"key": "C", "label": {"en": "Yangtze", "sk": "Jang-c'-ťiang"}},
                    {"key": "D", "label": {"en": "Mississippi", "sk": "Mississippi"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {
                    "en": "How many continents are there?",
                    "sk": "Koľko je kontinentov?"
                },
                "options": [
                    {"key": "A", "label": {"en": "5", "sk": "5"}},
                    {"key": "B", "label": {"en": "6", "sk": "6"}},
                    {"key": "C", "label": {"en": "7", "sk": "7"}},
                    {"key": "D", "label": {"en": "8", "sk": "8"}}
                ],
                "correct_key": "C"
            }
        ],
        "Science": [
            {
                "text": {
                    "en": "What is the chemical symbol for water?",
                    "sk": "Aká je chemická značka pre vodu?"
                },
                "options": [
                    {"key": "A", "label": {"en": "H2O", "sk": "H2O"}},
                    {"key": "B", "label": {"en": "CO2", "sk": "CO2"}},
                    {"key": "C", "label": {"en": "O2", "sk": "O2"}},
                    {"key": "D", "label": {"en": "N2", "sk": "N2"}}
                ],
                "correct_key": "A"
            },
            {
                "text": {
                    "en": "What is the speed of light?",
                    "sk": "Aká je rýchlosť svetla?"
                },
                "options": [
                    {"key": "A", "label": {"en": "300,000 km/s", "sk": "300 000 km/s"}},
                    {"key": "B", "label": {"en": "150,000 km/s", "sk": "150 000 km/s"}},
                    {"key": "C", "label": {"en": "450,000 km/s", "sk": "450 000 km/s"}},
                    {"key": "D", "label": {"en": "600,000 km/s", "sk": "600 000 km/s"}}
                ],
                "correct_key": "A"
            },
            {
                "text": {
                    "en": "Which planet is known as the Red Planet?",
                    "sk": "Ktorá planéta je známa ako Červená planéta?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Venus", "sk": "Venuša"}},
                    {"key": "B", "label": {"en": "Mars", "sk": "Mars"}},
                    {"key": "C", "label": {"en": "Jupiter", "sk": "Jupiter"}},
                    {"key": "D", "label": {"en": "Saturn", "sk": "Saturn"}}
                ],
                "correct_key": "B"
            }
        ],
        "Literature": [
            {
                "text": {
                    "en": "Who wrote 'Romeo and Juliet'?",
                    "sk": "Kto napísal 'Romeo a Júlia'?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Charles Dickens", "sk": "Charles Dickens"}},
                    {"key": "B", "label": {"en": "William Shakespeare", "sk": "William Shakespeare"}},
                    {"key": "C", "label": {"en": "Jane Austen", "sk": "Jane Austen"}},
                    {"key": "D", "label": {"en": "Mark Twain", "sk": "Mark Twain"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {
                    "en": "Which book begins with 'Call me Ishmael'?",
                    "sk": "Ktorá kniha začína slovami 'Volajte ma Izmael'?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Moby-Dick", "sk": "Moby-Dick"}},
                    {"key": "B", "label": {"en": "The Great Gatsby", "sk": "Veľký Gatsby"}},
                    {"key": "C", "label": {"en": "1984", "sk": "1984"}},
                    {"key": "D", "label": {"en": "Pride and Prejudice", "sk": "Pýcha a predsudok"}}
                ],
                "correct_key": "A"
            },
            {
                "text": {
                    "en": "Who is the author of Harry Potter series?",
                    "sk": "Kto je autorom série Harry Potter?"
                },
                "options": [
                    {"key": "A", "label": {"en": "J.R.R. Tolkien", "sk": "J.R.R. Tolkien"}},
                    {"key": "B", "label": {"en": "C.S. Lewis", "sk": "C.S. Lewis"}},
                    {"key": "C", "label": {"en": "J.K. Rowling", "sk": "J.K. Rowling"}},
                    {"key": "D", "label": {"en": "Roald Dahl", "sk": "Roald Dahl"}}
                ],
                "correct_key": "C"
            }
        ],
        "Mathematics": [
            {
                "text": {
                    "en": "What is 15% of 200?",
                    "sk": "Koľko je 15% z 200?"
                },
                "options": [
                    {"key": "A", "label": {"en": "20", "sk": "20"}},
                    {"key": "B", "label": {"en": "30", "sk": "30"}},
                    {"key": "C", "label": {"en": "40", "sk": "40"}},
                    {"key": "D", "label": {"en": "50", "sk": "50"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {
                    "en": "What is the value of π (pi) approximately?",
                    "sk": "Aká je približná hodnota π (pí)?"
                },
                "options": [
                    {"key": "A", "label": {"en": "2.14", "sk": "2,14"}},
                    {"key": "B", "label": {"en": "3.14", "sk": "3,14"}},
                    {"key": "C", "label": {"en": "4.14", "sk": "4,14"}},
                    {"key": "D", "label": {"en": "5.14", "sk": "5,14"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {
                    "en": "What is the square root of 144?",
                    "sk": "Aká je druhá odmocnina z 144?"
                },
                "options": [
                    {"key": "A", "label": {"en": "10", "sk": "10"}},
                    {"key": "B", "label": {"en": "11", "sk": "11"}},
                    {"key": "C", "label": {"en": "12", "sk": "12"}},
                    {"key": "D", "label": {"en": "13", "sk": "13"}}
                ],
                "correct_key": "C"
            }
        ],
        "Art": [
            {
                "text": {
                    "en": "Who painted the Mona Lisa?",
                    "sk": "Kto namaľoval Monu Lisu?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Michelangelo", "sk": "Michelangelo"}},
                    {"key": "B", "label": {"en": "Leonardo da Vinci", "sk": "Leonardo da Vinci"}},
                    {"key": "C", "label": {"en": "Raphael", "sk": "Raphael"}},
                    {"key": "D", "label": {"en": "Donatello", "sk": "Donatello"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {
                    "en": "What is the primary color that cannot be made by mixing?",
                    "sk": "Aká je primárna farba, ktorú nemožno vytvoriť miešaním?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Orange", "sk": "Oranžová"}},
                    {"key": "B", "label": {"en": "Green", "sk": "Zelená"}},
                    {"key": "C", "label": {"en": "Red", "sk": "Červená"}},
                    {"key": "D", "label": {"en": "Purple", "sk": "Fialová"}}
                ],
                "correct_key": "C"
            },
            {
                "text": {
                    "en": "Which art movement was Pablo Picasso associated with?",
                    "sk": "S ktorým umeleckým smerom bol Pablo Picasso spojený?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Impressionism", "sk": "Impresionizmus"}},
                    {"key": "B", "label": {"en": "Cubism", "sk": "Kubizmus"}},
                    {"key": "C", "label": {"en": "Surrealism", "sk": "Surrealizmus"}},
                    {"key": "D", "label": {"en": "Expressionism", "sk": "Expresionizmus"}}
                ],
                "correct_key": "B"
            }
        ],
        "Music": [
            {
                "text": {
                    "en": "How many strings does a standard guitar have?",
                    "sk": "Koľko strún má štandardná gitara?"
                },
                "options": [
                    {"key": "A", "label": {"en": "4", "sk": "4"}},
                    {"key": "B", "label": {"en": "5", "sk": "5"}},
                    {"key": "C", "label": {"en": "6", "sk": "6"}},
                    {"key": "D", "label": {"en": "7", "sk": "7"}}
                ],
                "correct_key": "C"
            },
            {
                "text": {
                    "en": "Who composed the Four Seasons?",
                    "sk": "Kto zložil Štyri ročné obdobia?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Mozart", "sk": "Mozart"}},
                    {"key": "B", "label": {"en": "Beethoven", "sk": "Beethoven"}},
                    {"key": "C", "label": {"en": "Vivaldi", "sk": "Vivaldi"}},
                    {"key": "D", "label": {"en": "Bach", "sk": "Bach"}}
                ],
                "correct_key": "C"
            },
            {
                "text": {
                    "en": "What does 'forte' mean in music?",
                    "sk": "Čo znamená 'forte' v hudbe?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Soft", "sk": "Ticho"}},
                    {"key": "B", "label": {"en": "Loud", "sk": "Hlasno"}},
                    {"key": "C", "label": {"en": "Fast", "sk": "Rýchlo"}},
                    {"key": "D", "label": {"en": "Slow", "sk": "Pomaly"}}
                ],
                "correct_key": "B"
            }
        ],
        "Sports": [
            {
                "text": {
                    "en": "How many players are on a soccer team on the field?",
                    "sk": "Koľko hráčov má futbalový tím na ihrisku?"
                },
                "options": [
                    {"key": "A", "label": {"en": "9", "sk": "9"}},
                    {"key": "B", "label": {"en": "10", "sk": "10"}},
                    {"key": "C", "label": {"en": "11", "sk": "11"}},
                    {"key": "D", "label": {"en": "12", "sk": "12"}}
                ],
                "correct_key": "C"
            },
            {
                "text": {
                    "en": "In which sport is the term 'love' used?",
                    "sk": "V ktorom športe sa používa termín 'love'?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Golf", "sk": "Golf"}},
                    {"key": "B", "label": {"en": "Tennis", "sk": "Tenis"}},
                    {"key": "C", "label": {"en": "Cricket", "sk": "Kriket"}},
                    {"key": "D", "label": {"en": "Baseball", "sk": "Bejzbal"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {
                    "en": "How many Olympic rings are there?",
                    "sk": "Koľko olympijských kruhov existuje?"
                },
                "options": [
                    {"key": "A", "label": {"en": "3", "sk": "3"}},
                    {"key": "B", "label": {"en": "4", "sk": "4"}},
                    {"key": "C", "label": {"en": "5", "sk": "5"}},
                    {"key": "D", "label": {"en": "6", "sk": "6"}}
                ],
                "correct_key": "C"
            }
        ],
        "Technology": [
            {
                "text": {
                    "en": "What does CPU stand for?",
                    "sk": "Čo znamená skratka CPU?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Central Process Unit", "sk": "Centrálna procesná jednotka"}},
                    {"key": "B", "label": {"en": "Central Processing Unit", "sk": "Centrálna procesorová jednotka"}},
                    {"key": "C", "label": {"en": "Computer Personal Unit", "sk": "Počítačová osobná jednotka"}},
                    {"key": "D", "label": {"en": "Central Processor Unit", "sk": "Centrálna procesorová jednotka"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {
                    "en": "Who founded Microsoft?",
                    "sk": "Kto založil Microsoft?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Steve Jobs", "sk": "Steve Jobs"}},
                    {"key": "B", "label": {"en": "Bill Gates", "sk": "Bill Gates"}},
                    {"key": "C", "label": {"en": "Mark Zuckerberg", "sk": "Mark Zuckerberg"}},
                    {"key": "D", "label": {"en": "Elon Musk", "sk": "Elon Musk"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {
                    "en": "What does 'HTTP' stand for?",
                    "sk": "Čo znamená 'HTTP'?"
                },
                "options": [
                    {"key": "A", "label": {"en": "HyperText Transfer Protocol", "sk": "HyperText Transfer Protocol"}},
                    {"key": "B", "label": {"en": "High Transfer Text Protocol", "sk": "High Transfer Text Protocol"}},
                    {"key": "C", "label": {"en": "HyperText Technical Protocol", "sk": "HyperText Technical Protocol"}},
                    {"key": "D", "label": {"en": "High Tech Transfer Protocol", "sk": "High Tech Transfer Protocol"}}
                ],
                "correct_key": "A"
            }
        ],
        "Cinema": [
            {
                "text": {
                    "en": "Which movie won the first Academy Award for Best Picture?",
                    "sk": "Ktorý film vyhral prvú cenu Akadémie za najlepší film?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Wings", "sk": "Krídla"}},
                    {"key": "B", "label": {"en": "The Jazz Singer", "sk": "Jazzový spevák"}},
                    {"key": "C", "label": {"en": "Sunrise", "sk": "Úsvit"}},
                    {"key": "D", "label": {"en": "Metropolis", "sk": "Metropolis"}}
                ],
                "correct_key": "A"
            },
            {
                "text": {
                    "en": "Who directed 'The Godfather'?",
                    "sk": "Kto režíroval 'Krstný otec'?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Martin Scorsese", "sk": "Martin Scorsese"}},
                    {"key": "B", "label": {"en": "Francis Ford Coppola", "sk": "Francis Ford Coppola"}},
                    {"key": "C", "label": {"en": "Steven Spielberg", "sk": "Steven Spielberg"}},
                    {"key": "D", "label": {"en": "Quentin Tarantino", "sk": "Quentin Tarantino"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {
                    "en": "In which year was the first 'Star Wars' movie released?",
                    "sk": "V ktorom roku bol vydaný prvý film 'Star Wars'?"
                },
                "options": [
                    {"key": "A", "label": {"en": "1975", "sk": "1975"}},
                    {"key": "B", "label": {"en": "1977", "sk": "1977"}},
                    {"key": "C", "label": {"en": "1979", "sk": "1979"}},
                    {"key": "D", "label": {"en": "1981", "sk": "1981"}}
                ],
                "correct_key": "B"
            }
        ],
        "Philosophy": [
            {
                "text": {
                    "en": "Who is known as the father of Western philosophy?",
                    "sk": "Kto je známy ako otec západnej filozofie?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Socrates", "sk": "Sokrates"}},
                    {"key": "B", "label": {"en": "Plato", "sk": "Platón"}},
                    {"key": "C", "label": {"en": "Aristotle", "sk": "Aristoteles"}},
                    {"key": "D", "label": {"en": "Pythagoras", "sk": "Pythagoras"}}
                ],
                "correct_key": "A"
            },
            {
                "text": {
                    "en": "What is the famous phrase by Descartes?",
                    "sk": "Aká je slávna fráza od Descarta?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Know thyself", "sk": "Poznaj seba samého"}},
                    {"key": "B", "label": {"en": "I think, therefore I am", "sk": "Myslím, teda som"}},
                    {"key": "C", "label": {"en": "Life is suffering", "sk": "Život je utrpenie"}},
                    {"key": "D", "label": {"en": "God is dead", "sk": "Boh je mŕtvy"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {
                    "en": "Who wrote 'The Republic'?",
                    "sk": "Kto napísal 'Ústavu'?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Socrates", "sk": "Sokrates"}},
                    {"key": "B", "label": {"en": "Plato", "sk": "Platón"}},
                    {"key": "C", "label": {"en": "Aristotle", "sk": "Aristoteles"}},
                    {"key": "D", "label": {"en": "Epicurus", "sk": "Epikuros"}}
                ],
                "correct_key": "B"
            }
        ],
        "Politics": [
            {
                "text": {
                    "en": "How many members are in the United Nations Security Council?",
                    "sk": "Koľko členov má Bezpečnostná rada OSN?"
                },
                "options": [
                    {"key": "A", "label": {"en": "10", "sk": "10"}},
                    {"key": "B", "label": {"en": "12", "sk": "12"}},
                    {"key": "C", "label": {"en": "15", "sk": "15"}},
                    {"key": "D", "label": {"en": "20", "sk": "20"}}
                ],
                "correct_key": "C"
            },
            {
                "text": {
                    "en": "Who was the first female Prime Minister of the United Kingdom?",
                    "sk": "Kto bola prvá ženská premiérka Spojeného kráľovstva?"
                },
                "options": [
                    {"key": "A", "label": {"en": "Margaret Thatcher", "sk": "Margaret Thatcher"}},
                    {"key": "B", "label": {"en": "Theresa May", "sk": "Theresa May"}},
                    {"key": "C", "label": {"en": "Angela Merkel", "sk": "Angela Merkel"}},
                    {"key": "D", "label": {"en": "Indira Gandhi", "sk": "Indira Gandhi"}}
                ],
                "correct_key": "A"
            },
            {
                "text": {
                    "en": "In which year was the European Union established?",
                    "sk": "V ktorom roku bola založená Európska únia?"
                },
                "options": [
                    {"key": "A", "label": {"en": "1985", "sk": "1985"}},
                    {"key": "B", "label": {"en": "1990", "sk": "1990"}},
                    {"key": "C", "label": {"en": "1993", "sk": "1993"}},
                    {"key": "D", "label": {"en": "2000", "sk": "2000"}}
                ],
                "correct_key": "C"
            }
        ]
    }
    
    # Add 4 more topics to reach 12 total
    for topic_name in ["Food", "Animals", "Space", "Mythology"]:
        if topic_name not in topic_ids:
            result = topics_col.insert_one({'name': topic_name, 'active': True})
            topic_ids[topic_name] = result.inserted_id
            print(f"  ✓ Created topic: {topic_name}")
    
    # Simple questions for additional topics
    additional_questions = {
        "Food": [
            {
                "text": {"en": "What is sushi traditionally wrapped in?", "sk": "Do čoho je tradične zabalené suši?"},
                "options": [
                    {"key": "A", "label": {"en": "Seaweed", "sk": "Morské riasy"}},
                    {"key": "B", "label": {"en": "Rice paper", "sk": "Ryžový papier"}},
                    {"key": "C", "label": {"en": "Lettuce", "sk": "Šalát"}},
                    {"key": "D", "label": {"en": "Banana leaves", "sk": "Banánové listy"}}
                ],
                "correct_key": "A"
            },
            {
                "text": {"en": "Which country is known for pizza?", "sk": "Ktorá krajina je známa pizzou?"},
                "options": [
                    {"key": "A", "label": {"en": "France", "sk": "Francúzsko"}},
                    {"key": "B", "label": {"en": "Italy", "sk": "Taliansko"}},
                    {"key": "C", "label": {"en": "Spain", "sk": "Španielsko"}},
                    {"key": "D", "label": {"en": "Greece", "sk": "Grécko"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {"en": "What is the main ingredient in guacamole?", "sk": "Aká je hlavná zložka guacamole?"},
                "options": [
                    {"key": "A", "label": {"en": "Avocado", "sk": "Avokádo"}},
                    {"key": "B", "label": {"en": "Tomato", "sk": "Paradajka"}},
                    {"key": "C", "label": {"en": "Pepper", "sk": "Paprika"}},
                    {"key": "D", "label": {"en": "Onion", "sk": "Cibuľa"}}
                ],
                "correct_key": "A"
            }
        ],
        "Animals": [
            {
                "text": {"en": "What is the largest land animal?", "sk": "Aké je najväčšie suchozemské zviera?"},
                "options": [
                    {"key": "A", "label": {"en": "Giraffe", "sk": "Žirafa"}},
                    {"key": "B", "label": {"en": "Elephant", "sk": "Slon"}},
                    {"key": "C", "label": {"en": "Rhinoceros", "sk": "Nosorožec"}},
                    {"key": "D", "label": {"en": "Hippopotamus", "sk": "Hroch"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {"en": "How many legs does a spider have?", "sk": "Koľko nôh má pavúk?"},
                "options": [
                    {"key": "A", "label": {"en": "6", "sk": "6"}},
                    {"key": "B", "label": {"en": "8", "sk": "8"}},
                    {"key": "C", "label": {"en": "10", "sk": "10"}},
                    {"key": "D", "label": {"en": "12", "sk": "12"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {"en": "What is the fastest land animal?", "sk": "Aké je najrýchlejšie suchozemské zviera?"},
                "options": [
                    {"key": "A", "label": {"en": "Lion", "sk": "Lev"}},
                    {"key": "B", "label": {"en": "Cheetah", "sk": "Gepard"}},
                    {"key": "C", "label": {"en": "Leopard", "sk": "Leopard"}},
                    {"key": "D", "label": {"en": "Tiger", "sk": "Tiger"}}
                ],
                "correct_key": "B"
            }
        ],
        "Space": [
            {
                "text": {"en": "What is the largest planet in our solar system?", "sk": "Ktorá je najväčšia planéta v našej slnečnej sústave?"},
                "options": [
                    {"key": "A", "label": {"en": "Saturn", "sk": "Saturn"}},
                    {"key": "B", "label": {"en": "Jupiter", "sk": "Jupiter"}},
                    {"key": "C", "label": {"en": "Neptune", "sk": "Neptún"}},
                    {"key": "D", "label": {"en": "Uranus", "sk": "Urán"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {"en": "How many moons does Earth have?", "sk": "Koľko mesiacov má Zem?"},
                "options": [
                    {"key": "A", "label": {"en": "0", "sk": "0"}},
                    {"key": "B", "label": {"en": "1", "sk": "1"}},
                    {"key": "C", "label": {"en": "2", "sk": "2"}},
                    {"key": "D", "label": {"en": "3", "sk": "3"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {"en": "What is the name of Earth's galaxy?", "sk": "Ako sa volá galaxia Zeme?"},
                "options": [
                    {"key": "A", "label": {"en": "Andromeda", "sk": "Andromeda"}},
                    {"key": "B", "label": {"en": "Milky Way", "sk": "Mliečna dráha"}},
                    {"key": "C", "label": {"en": "Whirlpool", "sk": "Vírivka"}},
                    {"key": "D", "label": {"en": "Sombrero", "sk": "Sombrero"}}
                ],
                "correct_key": "B"
            }
        ],
        "Mythology": [
            {
                "text": {"en": "Who is the king of the Greek gods?", "sk": "Kto je kráľom gréckych bohov?"},
                "options": [
                    {"key": "A", "label": {"en": "Zeus", "sk": "Zeus"}},
                    {"key": "B", "label": {"en": "Poseidon", "sk": "Poseidón"}},
                    {"key": "C", "label": {"en": "Hades", "sk": "Hádes"}},
                    {"key": "D", "label": {"en": "Apollo", "sk": "Apollón"}}
                ],
                "correct_key": "A"
            },
            {
                "text": {"en": "What was the name of Thor's hammer?", "sk": "Ako sa volalo kladivo Thora?"},
                "options": [
                    {"key": "A", "label": {"en": "Excalibur", "sk": "Excalibur"}},
                    {"key": "B", "label": {"en": "Mjolnir", "sk": "Mjolnir"}},
                    {"key": "C", "label": {"en": "Gungnir", "sk": "Gungnir"}},
                    {"key": "D", "label": {"en": "Trident", "sk": "Trojzubec"}}
                ],
                "correct_key": "B"
            },
            {
                "text": {"en": "Who was the Egyptian god of the sun?", "sk": "Kto bol egyptský boh slnka?"},
                "options": [
                    {"key": "A", "label": {"en": "Osiris", "sk": "Osiris"}},
                    {"key": "B", "label": {"en": "Anubis", "sk": "Anubis"}},
                    {"key": "C", "label": {"en": "Ra", "sk": "Ra"}},
                    {"key": "D", "label": {"en": "Horus", "sk": "Horus"}}
                ],
                "correct_key": "C"
            }
        ]
    }
    
    multilingual_questions.update(additional_questions)
    
    # Insert questions
    total_questions = 0
    for topic_name, questions in multilingual_questions.items():
        topic_id = topic_ids.get(topic_name)
        if not topic_id:
            continue
        
        for q_data in questions:
            questions_col.insert_one({
                'topic_id': topic_id,
                'text': q_data['text'],
                'options': q_data['options'],
                'correct_key': q_data['correct_key'],
                'active': True
            })
            total_questions += 1
    
    print(f"\n✅ Seeded {len(topic_ids)} topics and {total_questions} multilingual questions (EN + SK)")
    print(f"   Each topic has 3 questions in both English and Slovak")
    return list(topic_ids.values())


if __name__ == '__main__':
    seed_multilingual_database()

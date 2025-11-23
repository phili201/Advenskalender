import flask
from flask import Flask, session, render_template, request, redirect, jsonify
import json
import datetime
import os

app = Flask(__name__)
app.secret_key = 'fhuerh8e3ut'
VAPID_PUBLIC = 'MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEmJHSaFfXp6SkZxtyXD2GDKPetWXPIKEDrYuRm1lnwG_gLlytlm8WbPdsGxabz7DRPV6aiQ4oeS-OGYDilvFXvg'
VAPID_PRIVATE = "MHcCAQEEIMPcsVY1KoB4RWTJSnOHm8eai4tUVJOuZ1N1Buqkq-2DoAoGCCqGSM49AwEHoUQDQgAEmJHSaFfXp6SkZxtyXD2GDKPetWXPIKEDrYuRm1lnwG_gLlytlm8WbPdsGxabz7DRPV6aiQ4oeS-OGYDilvFXvg"
SUB_FILE = 'data/subscription.json'
today = datetime.date.today()
day = today.day
month = today.month

Questions = {
    (1, 12): {'question': "Welche Farbe hat der Weihnachtsbaum klassischerweise?", 'answer': 'Grün', 'letter': 'L'},
    (2, 12): {'question' : "Wie viele Kläppchen hat ein normaler Advenskalender?", 'answer': "24", 'letter': "e"},
    (3, 12): {'question' : "Welches Kind bring an Weihnachten immer die Geschenke? Das", 'answer': "Christkind", 'letter': "t"},
    (4, 12): {'question' : "Was hat Mama für ihren Advenskalender gemacht?", 'answer': "Apfelpunsch", 'letter': "z"},
    (5, 12): {'question' : "Wie nennt man das Haus, das man unter den Baum stellt", 'answer': "Krippe", 'letter': "t"},
    (6, 12): {'question' : "Welche Figur bringt heute Geschenke? ,,Der ", 'answer': "Nikolaus", 'letter': "e"},
    (7, 12): {'question' : "An welchem Tag ist der Domgottesdienst von Jakob und mir?(Datum: TT.MM)", 'answer': "19.12", 'letter': "r"},
    (8, 12): {'question' : "Welches Instrument spielt Mama bei dem Lied, dass wir immer an den Advenssonntagen singen?", 'answer': "Akkordeon", 'letter': "T"},
    (9, 12): {'question' : "Wie heißt das traditionelle Weihnachtslied ,,Stille Nacht, heilige ... ?", 'answer': "Nacht", 'letter': "a"},
    (10, 12): {'question' : "Woher kommt die Tradition mit den Advenskalendern?", 'answer': "Deutschland", 'letter': "g"},
    (11, 12): {'question' : "Wie viele Buchstaben hat das Wort ,,Weihnachten?", 'answer': "11", 'letter': "V"},
    (12, 12): {'question' : "Welche Geschenke bekam Jesus?(Antworten mit Komma und Leerzeichen nach dem Komma abgetrennt)(G, W, M)", 'answer': "Gold, Weihrauch, Myrrhe", 'letter': "o"},
    (13, 12): {'question' : "Was essen wir immer an Heiligabend", 'answer': "Ente", 'letter': "r"},
    (14, 12): {'question' : "Heiligaben ist in diesem Jahr, was für ein Tag?", 'answer': "Mittwoch", 'letter': "W"},
    (15, 12): {'question' : "Bis wann gehen unsere Ferien?(Datum:TT.MM)", 'answer': "04.01", 'letter': "e"},
    (16, 12): {'question' : "In welchem Land entstand der Brauch des Advenskranzes", 'answer': "Deutschland", 'letter': "i"},
    (17, 12): {'question' : "Das englische Wort für Weihnachten", 'answer': "Christmas", 'letter': "h"},
    (18, 12): {'question' : "Welche Nummer hat Mama in ihrem Advenskalender", 'answer': "18", 'letter': "n"},
    (19, 12): {'question' : "Welchen Film gucken wir an Heiligabend häufig? Familie (2 Wörter)", 'answer': "Heinz Becker", 'letter': "a"},
    (20, 12): {'question' : "Bringe die Buchstaben in die richtige Reihenfolge(hWnhcentiea)", 'answer': "Weihnachten", 'letter': "c"},
    (21, 12): {'question' : "Wie heißen die Häuser, die man in der Advenszeits backt?(Im Singular schreiben)", 'answer': "Lebkuchenhaus", 'letter': "h"},
    (22, 12): {'question' : "Was bedeutet das lateinische wort  ,,Adventus ?", 'answer': "Advent", 'letter': "t"},
    (23, 12): {'question' : "Der 23.12 is der letzte Tag vor?", 'answer': "Heiligabend", 'letter': "e"},
    (24, 12): {'question' : "Wie wird der 24. Dezember auch genannt", 'answer': "Heiligabend", 'letter': "n"},
}


def require_login():
    allowed_routes = ['login', 'register', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session.get('user_id'):
        return redirect('/login')

def load_users():
    with open('data/users.json', 'r') as f:
        return json.load(f)

def save_letter(user_id, day, letter):
    try:
        with open('data/progress.json', 'r') as f:
            progress = json.load(f)
    except FileNotFoundError:
        progress = {}
    
    if user_id not in progress:
        progress[user_id] = {}

    progress[user_id][str(day)] = letter

    with open('data/progress.json', 'w') as f:
        json.dump(progress, f)

def get_progress(user_id):
    if not user_id:
        return {}
    try:
        with open('data/progress.json', 'r') as f:
            progress = json.load(f)
            return progress.get(user_id, {})
    except FileNotFoundError:
        return {}

@app.route('/', methods=['POST', 'GET'])
def index():
    user_id = session.get('user_id')
    if 'user_id' not in session:
        return redirect('/login')
    today = datetime.date.today()
    day = today.day
    month = today.month
    progress = get_progress(user_id)
    entry = Questions.get((day, month), None)
    Feedback = None
    question = None
    letter = None
    if entry:
        question = entry['question']
        right_answer = entry['answer']
        letter = entry['letter']

        if request.method == 'POST':
            user_answer = request.form['answer'].strip()

            if user_answer.lower() == right_answer.lower():
                save_letter(user_id, day, letter)
                Feedback = f"Richtig! Du bekommst den Buchstaben: {letter}"
            else:
                Feedback = f"Falsch! Richtige Antwort ist: {right_answer}"
    else:
        question = None

    letters = []
    for key in sorted(progress.keys(), key=lambda x: int(''.join(filter(str.isdigit, str(x))))):
        letters.append(progress[key])
    loesungswort = ''.join(letters)
    letters_full = []
    for i in range(1, 25):
        key = str(i)
        letters_full.append(progress.get(key, None))

    return render_template(
        'index.html',
        question=question,
        Feedback=Feedback,
        loesungswort=loesungswort,
        now=today,
        letters_full=letters_full
    )

@app.route('/login', methods=['POST', 'GET'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        if username in users:
            if users[username]['password'] == password:
                session['user_id'] = username
                return redirect('/')
            else:
                message = 'Passwort falsch'
        else:
            message = 'User existiert nicht'
    return render_template('login.html', message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
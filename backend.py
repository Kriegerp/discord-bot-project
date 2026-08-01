from flask import Flask, jsonify, request
import subprocess
import random
import os
from dotenv import load_dotenv
from faapi import FAAPI
import sqlite3
import datetime
import google.generativeai as genai

load_dotenv()
FA_COOKIE_A = os.environ.get('FA_COOKIE_A')
FA_COOKIE_B = os.environ.get('FA_COOKIE_B')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Datenbank Initialisierung
DB_NAME = "data.db" # Name der Datenbank-Datei

def init_db():
    # Stellt eine Verbindung her (erstellt die Datei, falls sie fehlt)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Erstellt die Tabelle 'users', WENN sie noch nicht existiert
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 500,
        last_daily TEXT DEFAULT '2000-01-01 00:00:00'
    )
    ''')

    # Tabelle 'oc'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ocs (
        name TEXT PRIMARY KEY,
        age INTEGER DEFAULT 0,
        height TEXT DEFAULT '6ft',
        description TEXT DEFAULT 'Description here',
        picture TEXT DEFAULT 'URL'
    )
    ''')

    conn.commit() # Speichert die Änderungen
    conn.close() # Schließt die Verbindung
    print(f"Datenbank '{DB_NAME}' erfolgreich initialisiert.")

#Flask Anwendung
app = Flask(__name__)

fa_cookies_list = [
    {"name": "a", "value": FA_COOKIE_A},
    {"name": "b", "value": FA_COOKIE_B}
]

try:
    fa_client = FAAPI(cookies=fa_cookies_list)
    if fa_client.login_status:
        print("FAAPI-Client erfolgreich eingeloggt.")
    else:
        print("!!! FEHLER: FAAPI-Login fehlgeschlagen, obwohl Cookies übergeben wurden.")

except Exception as e:
    print(f"!!! FEHLER: FAAPI-Client konnte nicht initialisiert werden: {e}")

init_db()

# --- NEU: Gemini Client Konfiguration (Mit Modell-Listing) ---
gemini_model = None # Wichtig: Vor dem try definieren
try:
    print("Konfiguriere Gemini API...") # Debug
    genai.configure(api_key=GEMINI_API_KEY)
    
    # --- NEU: Verfügbare Modelle auflisten ---
    print("Versuche, verfügbare Gemini-Modelle aufzulisten...")
    available_models = []
    for m in genai.list_models():
        # Prüfe, ob das Modell 'generateContent' unterstützt
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            
    if not available_models:
        print("!!! FEHLER: Keine Modelle gefunden, die 'generateContent' unterstützen.")
    else:
        print(f"--- Verfügbare Modelle für generateContent: {available_models} ---")

    # Wähle das Modell - Versuche es weiter mit 1.0 Pro als Fallback
    # Wir könnten hier Logik einbauen, um eines aus der Liste zu wählen
    model_to_use = 'models/gemini-flash-latest' 
    print(f"Versuche, Modell '{model_to_use}' zu initialisieren...")
    gemini_model = genai.GenerativeModel(model_to_use)
    print(f"Gemini API erfolgreich konfiguriert mit Modell '{model_to_use}'.")

except Exception as e:
    import traceback # Importiere traceback hier
    print(f"!!! FEHLER: Konnte Gemini API nicht konfigurieren oder Modelle auflisten:")
    traceback.print_exc() # Drucke den vollen Fehler beim Konfigurieren
    gemini_model = None
# --- Gemini Ende ---


#Menüpunkte
@app.route("/hello")
def hallo_welt():
    # JSON Antwort
    return jsonify(greeting="Hello from Backend")

@app.route("/pi_status")
def get_pi_status():
        output_temp = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
        temp_string = output_temp.stdout.replace("temp=", "").replace("'C\n", "")

        output_storage = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        storage_string = output_storage.stdout.splitlines()[1].split()[4]

        return jsonify(temperatur=temp_string, storage=storage_string)

@app.route("/fa/<artist_name>")
def get_fa_submission(artist_name):
    try:
        # 1. Galerie holen (NUR SEITE 1)
        print(f"Calling first page of the gallery of {artist_name}...")
        gallery_page_data = fa_client.gallery(artist_name, page=1)
        
        # gallery_page_data ist ein Tuple: (submissions_list, next_page_number)
        submissions_list = gallery_page_data[0] 

        if not submissions_list:
            return jsonify(error=f"Gallery of '{artist_name}' is empty or not accessible."), 404

        # 2. Zufällige Submission von der ersten Seite auswählen
        random_sub_partial = random.choice(submissions_list)
        random_id = random_sub_partial.id

        # 3. Volle Submission-Details holen
        submission_data = fa_client.submission(random_id)
        submission = submission_data[0] # Wir wollen nur das Submission-Objekt

        # 4. Saubere JSON-Antwort für den Bot erstellen
        author_name = submission.author.name if hasattr(submission, 'author') and hasattr(submission.author, 'name') else artist_name
        image_link = submission.file_url

        return jsonify(
            artist=author_name,
            artist_url=f"https://www.furaffinity.net/user/{author_name.lower()}/",
            title=submission.title,
            image_url=image_link,
            submission_url=f"https://www.furaffinity.net/view/{submission.id}/"
        )
    
    except Exception as e:
        return jsonify(error=f"Ein Fehler ist aufgetreten: {type(e).__name__}: {e}"), 500

# Diese Hilfsfunktion stellt sicher, dass ein User existiert
def get_or_create_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Lässt uns Spalten nach Namen abrufen
    cursor = conn.cursor()
    
    # 1. Versuche, den User zu finden
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    
    if user_data:
        # User gefunden, gib Daten zurück
        conn.close()
        return user_data
    else:
        # 2. User nicht gefunden, neu erstellen (INSERT)
        print(f"User {user_id} nicht gefunden. Erstelle neuen Eintrag.")
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        
        # 3. Den neu erstellten User abrufen und zurückgeben
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        new_user_data = cursor.fetchone()
        conn.close()
        return new_user_data

# Der eigentliche Menüpunkt für !balance
@app.route("/balance/<int:user_id>")
def get_balance(user_id):
    try:
        user = get_or_create_user(user_id)
        # Wir geben den Kontostand als JSON zurück
        return jsonify(
            user_id=user['user_id'],
            balance=user['balance']
        )
    except Exception as e:
        return jsonify(error=f"Datenbankfehler: {e}"), 500
    
@app.route("/daily/<int:user_id>")
def claim_daily(user_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Nutzer holen 
        user = get_or_create_user(user_id)

        # 2. Zeitstempel aus der DB in ein Objekt umwandeln
        last_daily_str = user['last_daily']
        last_daily_time = datetime.datetime.strptime(last_daily_str, '%Y-%m-%d %H:%M:%S')
        
        jetzt = datetime.datetime.now()
        zeit_differenz = jetzt - last_daily_time

        # 3. Prüfen, ob 16 Stunden vergangen sind
        if zeit_differenz > datetime.timedelta(hours=16):
            # 4. JA! Zeit ist um. Datenbank aktualisieren.
            
            # Neuer Kontostand
            neuer_kontostand = user['balance'] + 500
            # Neuer Zeitstempel (als String für die DB)
            neuer_zeitstempel = jetzt.strftime('%Y-%m-%d %H:%M:%S')

            # --- HIER IST DER SQL-BEFEHL ---
            cursor.execute(
                "UPDATE users SET balance = ?, last_daily = ? WHERE user_id = ?",
                (neuer_kontostand, neuer_zeitstempel, user_id)
            )
            conn.commit() # Speichern!
            conn.close()

            # Erfolgsmeldung zurückgeben
            return jsonify(
                success=True,
                message=f"Successfully claimed your daily bonus! Your balance is now: {neuer_kontostand}"
            )

        else:
            # 5. NEIN! Zu früh.
            conn.close()
            
            # Berechne die verbleibende Zeit (optional, aber cool)
            verbleibend = datetime.timedelta(hours=24) - zeit_differenz
            stunden_verbleibend = int(verbleibend.total_seconds() // 3600)
            minuten_verbleibend = int((verbleibend.total_seconds() % 3600) // 60)

            return jsonify(
                success=False,
                message=f"Already claimed! Wait {stunden_verbleibend} hours and {minuten_verbleibend} minutes before claiming."
            )

    except Exception as e:
        return jsonify(error=f"Datenbankfehler: {type(e).__name__}: {e}"), 500

@app.route("/ocs/create", methods=['POST'])
def create_oc():
    try:
        data = request.json
        oc_name = data['name']

        # DB verbinden
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # INSERT
        cursor.execute("INSERT OR IGNORE INTO ocs (name) VALUES (?)", (oc_name,))

        conn.commit()
        conn.close()

        return jsonify(message=f"OC {oc_name} successfully added!")
    except Exception as e:
        return jsonify(error=f"Datenbankfehler: {type(e).__name__}: {e}"), 500

@app.route("/ocs/update", methods=['POST'])
def update_oc():
    try:
        data = request.json
        oc_name = data['name']
        field_to_update = data['field']
        new_value = data['value']

        # Sicherheitscheck
        # Allow only updates for known column to prevent SQL-injects
        allowed_fields = ["age", "height", "description", "picture"]
        if field_to_update not in allowed_fields:
            return jsonify(error=f"invalid field: '{field_to_update}'."), 400
        
        # connect DB
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Checks for existing OC
        cursor.execute("SELECT name FROM ocs WHERE name = ?", (oc_name,))
        existing_oc = cursor.fetchone()

        if not existing_oc:
            conn.close()
            return jsonify(error=f"OC '{oc_name}' nicht gefunden. Erstelle ihn zuerst mit `!oc create {oc_name}`."), 404

        # UPDATE command (only if OC exists)
        sql_command = f"UPDATE ocs SET {field_to_update} = ? WHERE name = ?"
        cursor.execute(sql_command, (new_value, oc_name))

        conn.commit()
        conn.close()

        print(f"OC {oc_name}: Set '{field_to_update}' to '{new_value}'.")
        return jsonify(message=f"OC '{oc_name}': Set {field_to_update} to '{new_value}'!")
    
    except Exception as e:
        return jsonify(error=f"Datenbankfehler beim Update: {type(e).__name__}: {e}"), 500
    
@app.route("/ocs/get/<name>")
def get_oc(name):
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # SELECT * (alle Spalten) für den gesuchten Namen
        cursor.execute("SELECT * FROM ocs WHERE name = ?", (name,))
        oc_data = cursor.fetchone()

        conn.close()

        if oc_data:
            # Found OC, transform row into Dictionary and return JSON
            oc_dict = dict(oc_data)
            return jsonify(oc_dict)
        else:
            # OC not found
            return jsonify(error=f"OC '{name}' not found")
    except Exception as e:
        return jsonify(error=f"Database error: {type(e).__name__}: {e}"), 500


@app.route("/ocs/delete/<name>", methods=['DELETE'])
def delete_oc(name):
    try:
        # DB verbinden
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check if OC exists
        # SELECT * (alle Spalten) für den gesuchten Namen
        cursor.execute("SELECT * FROM ocs WHERE name = ?", (name,))
        existing_oc = cursor.fetchone()

        if not existing_oc:
            conn.close()
            # 404
            return jsonify(error=f"OC '{name}' not found."), 404

        cursor.execute("DELETE FROM ocs WHERE name = ?", (name,))

        conn.commit()
        conn.close()

        print(f"OC {name} gelöscht.")
        return jsonify(message=f"OC {name} successfully deleted!"), 200
    
    except Exception as e:
        return jsonify(error=f"Datenbankfehler: {type(e).__name__}: {e}"), 500
    
@app.route("/ocs/list/")
def list_all_oc():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # SELECT
        cursor.execute("SELECT name FROM ocs")
        oc_data = cursor.fetchall()

        conn.close()

        name_list = []

        for row in oc_data:
            current_name = row['name']
            name_list.append(current_name)
            
        return jsonify(names=name_list)
        
    except Exception as e:
        return jsonify(error=f"Database error: {type(e).__name__}: {e}"), 500

@app.route("/oc_question/")
def get_oc_question():
    import traceback

    if gemini_model is None:
        print("Error: called get_oc_question, but gemini_model is None.")
        return jsonify(error="Gemini API is not configured."), 503 # Service Unavailable

    print("--- [DEBUG Backend] get_oc_question aufgerufen ---") # Debug
    try:
        prompt = (
            "Generate a single, fun, and relatively simple question about someone's original character (OC). "
            "The question should be easy to answer and spark creative, lighthearted thought. "
            "Avoid overly deep or philosophical topics. "
            "Examples of good questions: 'What's your OC's favorite snack?', "
            "'If your OC could have any mundane superpower (like perfectly parallel parking), what would it be?', "
            "'What song gets stuck in your OC's head most often?' "
            "Return ONLY the question itself, without any introduction or numbering."
        )
        print("--- [DEBUG Backend] Sende Prompt an Gemini... ---") # Debug
    
        # Rufe die Gemini API auf
        response = gemini_model.generate_content(prompt)

        # --- Drucke die *gesamte* Gemini-Antwort ---
        print(f"--- [DEBUG Backend] Rohe Gemini-Antwort:\n{response}\n---")

        # Extrahiere den Text der Antwort
        question = response.text.strip() # .strip() entfernt Leerzeichen am Anfang/Ende
        print(f"--- [DEBUG Backend] Extrahierte Frage: '{question}' ---") # Debug

        # Gib die Frage als JSON zurück
        return jsonify(question=question)

    except Exception as e:
        # --- Drucke den *kompletten* Traceback ---
        print(f"!!! FEHLER im get_oc_question try-Block:")
        traceback.print_exc() # Druckt den detaillierten Fehler ins Log
        return jsonify(error=f"Fehler bei der Kommunikation mit Gemini: {type(e).__name__}"), 500

@app.route("/economy/update/<int:user_id>", methods=['POST'])
def update_balance(user_id):
    import sqlite3
    data = request.json
    amount = data.get('amount', 0)
    START_CAPITAL = 500

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        if row:
            # user exists -> update
            new_balance = row[0] + amount
            cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        else:
            # user doesnt exist -> create
            new_balance = START_CAPITAL + amount
            cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, new_balance))

        conn.commit()
        conn.close()
        return jsonify(status="success", new_balance=new_balance)

    except Exception as e:
        return jsonify(status="error", message=str(e)), 500

@app.route("/economy/leaderboard")
def get_leaderboard():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Wir sortieren nach 'balance' absteigend (DESC) und nehmen nur die ersten 10
        cursor.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
        rows = cursor.fetchall()
        conn.close()

        # Umwandeln in eine Liste von Objekten
        leaderboard = [dict(row) for row in rows]
        return jsonify(leaderboard)
    except Exception as e:
        return jsonify(error=str(e)), 500


#Start Server (testing)
if __name__ == "__main__":
    #runs on Port 5000
    app.run('0.0.0.0', port=5000)
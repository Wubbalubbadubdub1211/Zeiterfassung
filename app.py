from flask import Flask, render_template, request, redirect #Flask: Web-Framework
from zeiteintrag import Zeiteintrag, db, Eintrag  # Import der Klasse
import os # Für Umgebungsvariablen

app = Flask(__name__) # Erste Flask-App
# eintraege = []  # Liste für Zeiteinträge

#PostgreSQL-Datenbank konfigurieren
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://arbeitszeit_user:3MNEhS2wmY8La19RfoPbIXg7jMHCrtzY@dpg-d1tmu6bipnbc73cgoj20-a.frankfurt-postgres.render.com/arbeitszeit')  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

db.init_app(app)  # Initialisierung der Datenbank

with app.app_context():  
    db.create_all()  # Erstellt die Datenbanktabellen, falls sie nicht existieren

@app.route("/", methods=["GET", "POST"]) # "/": Startseite der App, GET: Holt Seite oder Daten, POST: Senden von Daten
def index(): # Route für die Startseite
    if request.method == "POST":# Wenn das Formular abgeschickt wird
        # Eingaben aus dem Formular auslesen
        datum = request.form["datum"]
        startzeit = request.form["startzeit"]
        endzeit = request.form["endzeit"]

        # Zeiteintrag-Objekt erstellen
        zeiteintrag = Zeiteintrag(datum, startzeit, endzeit)
        #eintraege.append(eintrag.to_dict())  # Eintrag als dict speichern
        
        # In die Datenbank speichern
        neuer_eintrag = Eintrag(
            datum=zeiteintrag.datum,
            start=zeiteintrag.startzeit,
            ende=zeiteintrag.endzeit,
            stunden=zeiteintrag.stunden,
            gehalt=zeiteintrag.gehalt
        )
        db.session.add(neuer_eintrag)
        db.session.commit()

        return redirect("/")  # Zurück zur Startseite

    # Summen berechnen
    eintraege = Eintrag.query.all()
    gesamt_stunden = sum(e.stunden for e in eintraege)
    gesamt_gehalt = round(sum(e.gehalt for e in eintraege), 2)

    return render_template("index.html", eintraege=eintraege, # render_template: HTML-Seite rendern variable in html=Eingabe 
                           gesamt_stunden=gesamt_stunden,
                           gesamt_gehalt=gesamt_gehalt)

if __name__ == "__main__":
    app.run(debug=True)

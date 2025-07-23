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
            pausenzeit=zeiteintrag.pausenzeit,
            gehalt=zeiteintrag.gehalt
        )
        db.session.add(neuer_eintrag)
        db.session.commit()

        return redirect("/")  # Zurück zur Startseite

    monat = request.args.get("monat")  # Monat aus den URL-Parametern holen 
    if monat:
        # Wenn ein Monat angegeben ist, nur Einträge für diesen Monat anzeigen
        monat = monat.zfill(2)  # Monat auf 2 Stellen auffüllen
        eintraege = Eintrag.query.filter(Eintrag.datum.like(f"%-{monat}-%")).order_by(Eintrag.datum.desc()).all()
    else:
        # Ansonsten alle Einträge anzeigen
        eintraege = Eintrag.query.order_by(Eintrag.datum.desc()).all()

    # Summen berechnen
    gesamt_stunden = sum(e.stunden for e in eintraege)
    gesamt_gehalt = round(sum(e.gehalt for e in eintraege), 2)
    
    monat_name = {
    "01": "Januar", "02": "Februar", "03": "März", "04": "April",
    "05": "Mai", "06": "Juni", "07": "Juli", "08": "August",
    "09": "September", "10": "Oktober", "11": "November", "12": "Dezember"
}.get(monat, "") if monat else ""

    return render_template("index.html", eintraege=eintraege,
                       gesamt_stunden=gesamt_stunden,
                       gesamt_gehalt=gesamt_gehalt,
                       gewaehlter_monat=monat_name)


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    eintrag = Eintrag.query.get_or_404(id)  # Holt den Eintrag oder gibt 404 zurück, falls nicht gefunden
    db.session.delete(eintrag)              # Markiert den Eintrag zur Löschung
    db.session.commit()                     # Führt die Löschung in der Datenbank durch
    return redirect("/")                    # Leitet zurück auf die Startseite

if __name__ == "__main__":
    app.run(debug=True)

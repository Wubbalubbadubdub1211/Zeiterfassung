#region Importe & Initialisierung
from flask import Flask, render_template, request, redirect # Flask: Webseitenerstellung
from flask_sqlalchemy import SQLAlchemy # SQLAlchemy: Datenbankzugriff
from zeiteintrag import Zeiteintrag, db, Eintrag 
import os #um Umgebungsvariablen zu lesen
#endregion


#region App-Konfiguration & Datenbank-Setup
app = Flask(__name__)

# PostgreSQL-Datenbank konfigurieren
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://arbeitszeit_user:3MNEhS2wmY8La19RfoPbIXg7jMHCrtzY@dpg-d1tmu6bipnbc73cgoj20-a.frankfurt-postgres.render.com/arbeitszeit'
) # Wenn die Umgebungsvariable "DATABASE_URL" gefunden wird, wird sie verwendet, andernfalls die lokale URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Deaktiviert die Modifikations-Tracker, um Speicher zu sparen
db.init_app(app) # initialisiert die SQLAlchemy-Datenbank (db=SQLAlchemy()) mit der Flask-App

with app.app_context(): # Gibt  an, dass man im Kontext der App arbeitet
    db.create_all() # Erstellt die Datenbanktabellen, falls sie noch nicht existieren
#endregion

#region Route: Startseite    
@app.route("/") # wird auf die Starteseite geleitet, wenn die domain aufgerufen wird
def home():
    return redirect("/start")
    
@app.route("/start") # Route für die Startseite
def startseite():
    return render_template("startseite.html")
#endregion

#region Route: Menü: Arbeitszeiterfassung mit Formular & Monatsfilter
@app.route("/arbeitszeiterfassung", methods=["GET", "POST"]) # Menü "Arbeitszeiterfassung" wird aufgerufen
def index(): # wird aufgerufen, wenn die Startseite besucht wird
    if request.method == "POST": # Wenn das Formular abgeschickt wird, werden die Daten ausgelesen
        datum = request.form["datum"] 
        startzeit = request.form["startzeit"]
        endzeit = request.form["endzeit"]

        zeiteintrag = Zeiteintrag(datum, startzeit, endzeit) # ausgelesene Daten werden in ein Zeiteintrag-Objekt umgewandelt

        neuer_eintrag = Eintrag( # Erstellt einen neuen Eintrag in der Datenbank, Eintrag ist das Datenbankmodell (siehe zeiteintrag.py)
            datum=zeiteintrag.datum,
            start=zeiteintrag.startzeit,
            ende=zeiteintrag.endzeit,
            stunden=zeiteintrag.stunden,
            pausenzeit=zeiteintrag.pausenzeit,
            gehalt=zeiteintrag.gehalt
        )
        db.session.add(neuer_eintrag) # add bezeichnet, dass ein neuer Eintrag zur Datenbank hinzugefügt werden soll
        db.session.commit() # commit speichert die Änderungen in der Datenbank

        return redirect("/") # Nach dem Speichern wird die Startseite neu geladen
    
    # Monatsfilter: Wenn ein Monat ausgewählt ist, werden nur die Einträge dieses Monats angezeigt
    monat = request.args.get("monat") # holt den ausgewählten Monat aus der URL-Parameter
    if monat: # Wenn ein Monat ausgewählt wurde
        monat = monat.zfill(2) # Stellt sicher, dass der Monat immer zweistellig ist (z.B. "01" für Januar)
        eintraege = Eintrag.query.filter( 
            Eintrag.datum.like(f"%-{monat}-%")
        ).order_by(Eintrag.datum.desc()).all() # Filtert die Einträge nach dem ausgewählten Monat und sortiert sie absteigend nach Datum
    else:
        eintraege = Eintrag.query.order_by(Eintrag.datum.desc()).all() # Wenn kein Monat ausgewählt wurde, werden alle Einträge absteigend nach Datum sortiert

    monat_name = { # Dictionary, um den Monatsnamen aus der Monatszahl zu erhalten
        "":"", "01": "Januar", "02": "Februar", "03": "März", "04": "April",
        "05": "Mai", "06": "Juni", "07": "Juli", "08": "August",
        "09": "September", "10": "Oktober", "11": "November", "12": "Dezember"
    }.get(monat, "") if monat else "" 

    gesamt_stunden = sum(e.stunden for e in eintraege) # Berechnet die Gesamtstunden aller Einträge
    gesamt_gehalt = round(sum(e.gehalt for e in eintraege), 2) # Berechnet das Gesamtgehalt aller Einträge und rundet es auf 2 Dezimalstellen

    return render_template("index.html",
        eintraege=eintraege,
        gesamt_stunden=gesamt_stunden,
        gesamt_gehalt=gesamt_gehalt,
        gewaehlter_monat=monat_name
    ) # gibt die Daten an das Template "index.html" weiter
#endregion


#region Route: Eintrag löschen
@app.route("/delete/<int:id>", methods=["POST"]) # Route zum Löschen eines Eintrags, <int:id> ist die ID des Eintrags
def delete(id): 
    eintrag = Eintrag.query.get_or_404(id) # Holt den Eintrag mit der angegebenen ID oder gibt einen 404-Fehler zurück, wenn er nicht gefunden wird
    db.session.delete(eintrag)
    db.session.commit()
    return redirect("/")
#endregion


#region Lokaler Start der App
if __name__ == "__main__": 
    app.run(debug=True) # Startet die Flask-App im Debug-Modus, damit Änderungen sofort sichtbar sind
#endregion

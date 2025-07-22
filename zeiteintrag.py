from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import delete

class Zeiteintrag:
    PAUSEN_GRENZE1 = 6  
    PAUSEN_GRENZE2 = 7
    PAUSE1 = 0.5
    PAUSE2 = 1.0        

    def __init__(self, datum, startzeit, endzeit, stundensatz=13.25):
        self.datum = datum
        self.startzeit = startzeit
        self.endzeit = endzeit
        self.stundensatz = stundensatz
        self.stunden, self.pausenzeit = self._berechne_stunden()
        self.gehalt = round(self.stunden * self.stundensatz, 2)

    def _berechne_stunden(self):
        start = datetime.strptime(self.startzeit, "%H:%M")
        ende = datetime.strptime(self.endzeit, "%H:%M")
        stunden = (ende - start).seconds / 3600
        pausenzeit = 0.0
        
        if stunden > self.PAUSEN_GRENZE2:
            stunden -= self.PAUSE2
            pausenzeit += self.PAUSE2
        elif stunden > self.PAUSEN_GRENZE1:
            stunden -= self.PAUSE1
            pausenzeit = self.PAUSE1
        return round(stunden, 2), pausenzeit

    def to_dict(self):
        return {
            "datum": self.datum,
            "start": self.startzeit,
            "ende": self.endzeit,
            "stunden": self.stunden,
            "pausenzeit": self.pausenzeit,
            "gehalt": self.gehalt
        }
        


db = SQLAlchemy() # Initialisierung der Datenbank

class Eintrag(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Primärschlüssel für die Tabelle
    datum = db.Column(db.String(10), nullable=False) # Datum des Eintrags
    start = db.Column(db.String(5), nullable=False) # Startzeit des Eintrags
    ende = db.Column(db.String(5), nullable=False) # Endzeit des Eintrags
    stunden = db.Column(db.Float, nullable=False) # Gearbeitete Stunden
    pausenzeit = db.Column(db.Float, nullable=False)
    gehalt = db.Column(db.Float, nullable=False) # Verdientes Gehalt
    

    

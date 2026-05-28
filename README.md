# Movie Ticket Manager
Für unser objektorientiertes Programmierprojekt haben wir uns für einen Movie Ticket Manager entschieden. Ziel des Projekts ist die Entwicklung einer benutzerfreundlichen Webanwendung, mit der Kinotickets bequem online im Voraus gekauft werden können. Dadurch sollen Wartezeiten an der Kinokasse reduziert und die Mitarbeitenden des Kinos entlastet werden.

Die Anwendung richtet sich sowohl an Kinobesucher (Kunden) als auch an Mitarbeitende des Kinos (Admin). Sie wird als browserbasierte Webanwendung mit Frontend, Backend und Datenbank umgesetzt.

### Szenario
Im Movie Ticket Manager können die Kunden:
- aktuelle Filme einsehen
- ein Kundenkonto anlegen
- mehrere Tickets kaufen (inkl. Sitzplatzauswahl und Rabatten)
- das Filmangebot filtern (z.B. Sprache, Altersfreigabe)
- Filme bewerten
- Filme in ihrer persönlichen Liste speichern

Im Movie Ticket Manager können Admins:
- Filme hinzufügen, bearbeiten und löschen
- Vorstellungen mit Datum, Uhrzeit und Saal verwalten
- einsehen, wie viele Tickets pro Film verkauft wurden und welche Sitzplätze belegt sind

---

## User-Stories

### Kunde
| ID | User Story | Priorität | Status | Input | Output |
|---|---|---|---|---|---|
| US-01 | Als Kunde möchte ich die aktuellen Filme sehen, damit ich informiert Tickets kaufen kann. | Hoch | Umgesetzt | – | Filmliste (Titel, Bild, Kategorie, Sprache) `List[Film]` |
| US-02 | Als Kunde möchte ich ein Konto anlegen können, damit ich all meine Käufe einfach verwalten kann. | Hoch | Umgesetzt | Vorname`[String]`, Nachname`[String]`, E-Mail`[String]`, Passwort`[String]`, Geburtsdatum`[Date]`, Adresse`[String]`, Zahlungsart`[String]` | Kontobestätigung `[Boolean]` |
| US-03 | Als Kunde möchte ich Tickets kaufen können, damit ich die Tickets bequem im Voraus besorgen kann und mir den Zugang ins Kino vereinfachen kann. | Hoch | Umgesetzt | Film-ID`[UUID]`, Vorstellungs-ID`[UUID]`, Anzahl Tickets`[Int]`, Zahlungsart`[String]` | Bestellbestätigung `[Boolean]`, Bestellübersicht `[String]` |
| US-04 | Als Kunde möchte ich Sitzplätze auswählen können, damit ich entscheiden kann, wo ich sitze. | Hoch | Umgesetzt | Vorstellungs-ID`[UUID]`, Sitzplatz`[String]` | Bestätigter Sitzplatz `[String]`, Sitzplatz als belegt markiert `[Boolean]` |
| US-05 | Als Kunde möchte ich die Filme auf der Webseite sortieren und filtern können, da ich damit meine Suche nach Filmen verfeinern kann. | Mittel | Umgesetzt | Kategorie`[String]`, Sprache`[String]`, Altersfreigabe`[Int]`, Suchtitel`[String]` | Gefilterte Filmliste `[List[Film]]` |
| US-06 | Als Kunde möchte ich Rabatte (Student, Senior, Kind) auswählen können, damit ich den vergünstigten Preis erhalte. | Mittel | Umgesetzt | Rabatt-Typ`[String]` | Aktualisierter Ticketpreis `[Float]` |
| US-07 | Als Kunde möchte ich Snacks zum Ticket hinzufügen können, damit ich mein Kinoerlebnis bequem planen kann. | Niedrig | Umgesetzt | Snack-Auswahl`[String]`, Anzahl`[Int]` | Snack hinzugefügt `[Boolean]`, Gesamtpreis aktualisiert `[Float]` |
| US-08 | Als Kunde möchte ich nach dem Kauf eine Bestellübersicht sehen, damit ich alle Details meines Tickets auf einen Blick habe. | Hoch | Umgesetzt | – | Filmtitel`[String]`, Saal`[String]`, Sitzplatz`[String]`, Datum`[Date]`, Uhrzeit`[Time]`, Anzahl Tickets`[Int]`, Gesamtpreis`[Float]` |
| US-09 | Als Kunde möchte ich Filme bewerten können, damit ich meine Meinung teilen kann. | Niedrig | Umgesetzt | Sternebewertung`[Int]`, Kommentar`[String]` | Gespeicherte Bewertung `[Boolean]` |

### Admin
| ID | User Story | Priorität | Status | Input | Output |
|---|---|---|---|---|---|
| AS-01 | Als Admin möchte ich neue Filme hinzufügen können, damit das Filmprogramm aktuell angezeigt wird. | Hoch | Umgesetzt | Titel`[String]`, Beschreibung`[String]`, Kategorie`[String]`, Sprache`[String]`, Altersfreigabe`[Int]`, Coverbild`[String]`, Erscheinungsjahr`[Int]` | Neuer Film in der Datenbank `[Boolean]` |
| AS-02a | Als Admin möchte ich bestehende Filme bearbeiten können, damit falsche Informationen korrigiert werden können. | Hoch | Umgesetzt | Film-ID`[UUID]`, Titel`[String]`, Beschreibung`[String]`, Kategorie`[String]`, Sprache`[String]`, Altersfreigabe`[Int]`, Coverbild`[String]`, Erscheinungsjahr`[Int]` | Aktualisierter Film in der Datenbank `[Boolean]` |
| AS-02b | Als Admin möchte ich Filme löschen können, damit veraltete Einträge entfernt werden. | Hoch | Umgesetzt | Film-ID`[UUID]` | Film gelöscht `[Boolean]` |
| AS-03 | Als Admin möchte ich die Ticketverkäufe eines Films einsehen. Dabei sollen Informationen wie Anzahl verkaufter Tickets und Einnahmen pro Film angezeigt werden, um die Auslastung und Beliebtheit der Filme zu überwachen. | Hoch | Umgesetzt | – | Anzahl Tickets`[Int]`, Umsatz pro Film`[Float]` |
| AS-04 | Als Admin kann ich Filmvorstellungen verwalten, indem ich Datum, Uhrzeit und den zugehörigen Saal erstellen, bearbeiten oder löschen kann. Dadurch können Spielzeiten flexibel geplant und angepasst werden. | Hoch | Umgesetzt | Datum`[Date]`, Uhrzeit`[Time]`, Saal`[String]` | Vorstellung erstellt/aktualisiert/gelöscht `[Boolean]` |

### Allgemein
| ID | User Story | Priorität | Status | Input | Output |
|---|---|---|---|---|---|
| GS-01 | Als allgemeiner Benutzer (Admin oder Kunde) möchte ich mich in die Applikation einloggen können, um die verfügbaren Funktionen nutzen zu können. | Hoch | Umgesetzt | E-Mail`[String]`, Passwort`[String]` | Anmeldung erfolgreich `[Boolean]` |

---

## Use Cases
(Diagramm)

### Main Use Cases
**Kunde**
- Filme anzeigen
- Filme filtern und sortieren (z. B. nach Kategorie, Sprache, Altersfreigabe)
- Konto anlegen
- Einloggen / Ausloggen
- Tickets kaufen
- Sitzplatz auswählen
- Mehrere Tickets gleichzeitig kaufen
- Rabatte auswählen (Student, Kind, Senior)
- Snacks zum Ticket hinzufügen
- Bestellübersicht anzeigen
- Filme bewerten
- Filme zur persönlichen Liste hinzufügen

**Admin**
- Einloggen / Ausloggen
- Filme hinzufügen
- Filme bearbeiten
- Filme löschen
- Informationen zum Film verwalten (Datum, Uhrzeit, Saal)
- Ticketverkäufe / Verfügbarkeit einsehen (z. B. Anzahl pro Film)
- Übersicht über gebuchte Plätze anzeigen

### Rollen
- Kunden (Nutzt die Anwendung zum Suchen, Bewerten und Kaufen von Filmen)
- Admin (Mitarbeitende Kino; Verwaltet Inhalte und überwacht das System)

---

## Funktionsübersicht
Die Anwendung bietet folgende Funktionen:
**Filme anzeigen**
- Titel
- Beschreibung
- Altersfreigabe
- Coverbild
- Hauptdarsteller
- Erscheinungsjahr / Datum
- Kategorie (Comedy, Romance, Sci-Fi, Fantasy)
- Sprache (In welcher Sprache der Film im Kino verfügbar ist)

**Kundenkonto anlegen**
- Vorname
- Nachname
- Adresse
- PLZ
- Geburtsdatum
- Alter (wird vom Geburtsdatum berechnet, der Kunde muss nur sein Geburtsdatum eingeben beim Anlegen eines Kontos)
- Telefonnummer
- E-Mail
- Passwort
- Zahlungsart (Karte, Rechnung, TWINT)

**Kunden können Tickets kaufen**
- Es können mehrere Tickets gekauft werden
- Es gibt Senioren-, Studenten- und Kindervergünstigung
- Zu den Tickets können Snacks mitgebucht werden

**Sitzplatz**
- Einteilung in Sektor A, B und C (alternativ: Direkteingabe wie „21C", falls kein visueller Sitzplan vorhanden)
- Verfügbare Sitzplätze werden dem Kunden visuell angezeigt (z. B. als interaktiver Sitzplan oder Dropdown-Menü)
- Sitzplatzverfügbarkeit wird im System gespeichert und in Echtzeit aktualisiert
- Beim Ticketkauf wird jedem Kunden ein Sitzplatz fest zugeteilt und als belegt markiert

**Bewertungen**
- Kunden können einen Film nach dem Kauf eines Tickets bewerten (Sternebewertung 1–5 oder Kommentar)

**Persönliche Filmliste**
- Kunden können Filme in ihrer persönlichen Merkliste speichern

**Filmsuche und Filter**
- Kunden können das Filmangebot nach Sprache, Kategorie und Altersfreigabe filtern

**Bestellübersicht**

Nach jedem Ticketkauf erhält der Kunde automatisch eine Bestellübersicht mit folgenden Informationen:
- Filmtitel
- Saal und Sitzplatz
- Ort
- Datum und Uhrzeit
- Anzahl der gekauften Tickets
- Gesamtpreis

**Admin-Funktionen**
- Admins können Filme hinzufügen, bearbeiten und löschen
- Admins können Vorstellungen mit Datum, Uhrzeit und Saal verwalten
- Admins können einsehen, wie viele Tickets pro Film verkauft wurden und welche Sitzplätze belegt sind

---

## Architektur
<img width="3368" height="1724" alt="image" src="https://github.com/user-attachments/assets/be67a122-66b0-49b1-b1cb-4a5317c641ae" />


### Schichten
- Frontend: UI/Benutzerinteraktion mittels NiceGUI
- Backend: Businesslogik mittels Services
- Datenpersistenz: Repositories, SQLite, ORM und DAO 

### Designentscheidung
- MVC Struktur (Model-View-Controller) -> in unserem Fall Services statt Controller
- Mittels MVC hat man eine klare Struktur und Gliederung der drei Schichten

### Verwendete Designmuster
- Das Frontend kommuniziert ausschließlich mit den Service-Klassen und greift nicht direkt auf die Datenbank bzw. die Repository-Schicht zu. Dadurch bleibt die Anwendung klar strukturiert und die Verantwortlichkeiten sind sauber getrennt.
- Die Service-Klassen enthalten die gesamte Businesslogik der Anwendung. Sie verarbeiten Anfragen aus dem Frontend, führen Validierungen durch und koordinieren den Zugriff auf die Daten.
- Im Frontend ist die gesamte Benutzerinteraktion implementiert. Dazu gehören die Darstellung der Benutzeroberfläche, Eingaben der Benutzer sowie die Kommunikation mit dem Backend.
- Die Service-Schicht verwendet die Repository-Klassen für den Zugriff auf die Datenbank.
- Die Repository-Klassen kapseln sämtliche Datenbankoperationen (CRUD – Create, Read, Update, Delete). Dadurch bleibt der Datenzugriff zentral verwaltet und unabhängig von der Businesslogik.
- Die Model-Klassen definieren die ORM-Modelle und bilden die Struktur der Datenbanktabellen ab. Sie repräsentieren die zentralen Datenobjekte der Anwendung.

---

## Datenbank und ORM
<img width="5328" height="5564" alt="image" src="https://github.com/user-attachments/assets/0ad26bb0-b85c-4b19-819e-6b3ac5218ae5" />


### Einheiten
- Ticket
- Film
- Sitzplatz
- Account
- Kunde
- Kategorie
- Sprache
- Zahlungsart
- Bestellung
- Vorstellung
- Snack
- Bewertung
  
### Beziehungen
- Ein Kunde kann mehrere Bewertungen erstellen.
- Jede Bewertung wird von genau einem Kunden erstellt.
- Ein Film kann mehrere Bewertungen haben.
- Jede Bewertung gehört genau zu einem Film.
- Ein Film hat eine Sprache.
- Eine Sprache kann mehreren Filmen zugeordnet sein.
- Ein Film gehört zu einer Kategorie.
- Eine Kategorie kann mehrere Filme enthalten.
- Ein Admin-Account kann mehrere Filme verwalten.
- Ein Film kann von einem Admin-Account verwaltet werden.
- Ein Admin-Account kann mehrere Vorstellungen verwalten.
- Eine Vorstellung wird von einem Admin-Account verwaltet.
- Eine Vorstellung hat mehrere Sitzplätze.
- Ein Sitzplatz gehört zu genau einer Vorstellung.
- Ein Kunde wählt eine Zahlungsart.
- Eine Zahlungsart kann von mehreren Kunden verwendet werden.
- Ein Kunde kann mehrere Bestellungen machen.
- Jede Bestellung gehört genau zu einem Kunden.
- Eine Bestellung beinhaltet mehrere Tickets.
- Ein Ticket gehört genau zu einer Bestellung.
- Ein Ticket kann mehrere Snacks beinhalten.
- Ein Snack kann in mehreren Tickets enthalten sein.
- Eine Vorstellung kann mehrere Tickets haben.
- Jedes Ticket gehört zu genau einer Vorstellung.
- Ein Film kann mehrere Vorstellungen haben.
- Eine Vorstellung zeigt genau einen Film.


---

## Datentypen
| Feldname | Beschreibung | Datentyp | Pflichtfeld | Beispiel |
|---|---|---|---|---|
| Ticket-ID | Eindeutige ID eines Tickets, die zur eindeutigen Zuordnung und Verwaltung im System dient | Int | Ja | 12345678 |
| Kunden-ID | Durch das Anlegen des Kundenkontos wird die Kundennummer generiert | Int | Ja | 9876 |
| Film-ID | Eindeutige ID eines Films zur Verwaltung im System | Int | Ja | 1 |
| Sitzplatz | Bezeichnung des Sitzplatzes im Kinosaal (Reihe + Platznummer) zur Auswahl und Reservierung | String | Ja | A09 |
| Preis | Ticketpreis, den der Kunde bezahlt | Float | Ja | 15.90 |
| Vorstellungs-ID | Eindeutige ID einer Filmvorstellung (Datum, Uhrzeit, Saal) zur Verwaltung im System | Int | Ja | 111 |
| Bewertung | Sternebewertung eines Films durch den Kunden | Int | Nein | 4 |
| Rabatt-Typ | Art des gewählten Rabatts beim Ticketkauf | String | Nein | Student |
| Snack | Bezeichnung des gewählten Snacks zum Ticket | String | Nein | Popcorn |
| Zahlungsart | Vom Kunden gewählte Zahlungsmethode | String | Ja | TWINT |

---

## Erwartetes Format
| Output | Beschreibung | Format | Empfänger |
|---|---|---|---|
| Bestellübersicht | Zusammenfassung nach Ticketkauf (Filmtitel, Saal, Sitzplatz, Datum, Uhrzeit, Anzahl Tickets, Gesamtpreis) | Webseite | Kunde |
| Filmliste | Alle verfügbaren Filme mit Details (Titel, Bild, Kategorie, Sprache, Altersfreigabe) | Webseite | Kunde |
| Bewertungsanzeige | Gespeicherte Sternebewertung und Kommentar auf der Filmseite | Webseite | Kunde, Admin |
| Ticketverkauf-Übersicht | Anzahl verkaufter Tickets pro Film | Webseite | Admin |
| Sitzplatzbelegung | Übersicht belegte und freie Sitzplätze pro Vorstellung | Webseite | Admin |
| Kontobestätigung | Bestätigung nach erfolgreicher Registrierung | Webseite | Kunde |

---

## Repository-Struktur

```
movie_ticket_manager/
│
├── main.py                          # Einstiegspunkt – startet die NiceGUI-App
├── requirements.txt                 # Python-Abhängigkeiten
│
├── config/
│   └── database.py                  # Datenbankverbindung (SQLite) & Engine-Setup
│
├── backend/
│   ├── seed.py                      # Testdaten (Filme, Kunden, Vorstellungen, Sitzplätze)
│   │
│   ├── models/                      # Domain-Modelle (reine Python-Klassen)
│   │   ├── account.py
│   │   ├── bestellung.py
│   │   ├── bewertung.py
│   │   ├── film.py
│   │   ├── kunde.py
│   │   ├── sitzplatz.py
│   │   ├── snack.py
│   │   ├── ticket.py
│   │   ├── vorstellung.py
│   │   ├── enums.py                 # Enumerations (Vergünstigungsart, Rolle, …)
│   │   └── orm/                     # ORM-Modelle (SQLModel-Tabellen)
│   │       ├── account_sql.py
│   │       ├── bestellung_sql.py
│   │       ├── bewertung_sql.py
│   │       ├── film_sql.py
│   │       ├── kategorie_sql.py
│   │       ├── kunde_sql.py
│   │       ├── sitzplatz_sql.py
│   │       ├── snack_sql.py
│   │       ├── sprache_sql.py
│   │       ├── ticket_sql.py
│   │       ├── ticket_snack_sql.py
│   │       ├── vorstellung_sql.py
│   │       └── zahlungsart_sql.py
│   │
│   ├── repositories/                # Datenzugriff (CRUD-Operationen)
│   │   ├── account_repository.py
│   │   ├── bestellung_repository.py
│   │   ├── bewertung_repository.py
│   │   ├── film_repository.py
│   │   ├── kunde_repository.py
│   │   ├── snack_repository.py
│   │   └── user_repository.py
│   │
│   └── services/                    # Businesslogik
│       ├── admin_service.py         # Film- und Vorstellungsverwaltung (Admin)
│       ├── bestellung_service.py    # Ticketkauf, Sitzplatzverwaltung
│       ├── film_service.py          # Filmsuche, Filter, Bewertungen
│       └── user_service.py          # Registrierung, Login, Profil
│
└── frontend/
    ├── auth.py                      # Session-Management (Login-State, Rollen)
    ├── components.py                # Wiederverwendbare UI-Komponenten (Navbar, …)
    ├── services.py                  # Brücke Frontend ↔ Backend-Services
    ├── pdf_ticket.py                # PDF-Ticket-Generierung (reportlab)
    │
    └── pages/                       # NiceGUI-Seiten (je Route eine Datei)
        ├── filme.py                 # Startseite – Filmübersicht & Filter
        ├── film_detail.py           # Filmdetailseite & Bewertungen
        ├── checkout.py              # Sitzplatzauswahl, Snacks, Ticketkauf
        ├── profil.py                # Kundenprofil & Bestellhistorie
        ├── login.py                 # Anmeldeseite
        ├── register.py              # Registrierungsseite
        └── admin.py                 # Admin-Panel (Filme, Vorstellungen, Umsatz)
```

---

## How-to Programm starten

### Voraussetzungen
- Python **3.11 oder höher** muss installiert sein
- Empfohlen: Python 3.13

### 1. Repository klonen
```bash
git clone <repository-url>
cd movie_ticket_manager
```

### 2. Virtuelle Umgebung erstellen und aktivieren

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

Die `requirements.txt` enthält:
- `nicegui` – Web-UI-Framework
- `sqlmodel` – ORM & Datenbankzugriff (basiert auf SQLAlchemy + Pydantic)
- `reportlab` – PDF-Ticket-Generierung

### 4. Anwendung starten
```bash
python main.py
```

Beim ersten Start wird die Datenbank automatisch erstellt und mit Testdaten befüllt (Seed). Anschliessend erscheint in der Konsole eine URL:

```
NiceGUI ready to go on http://localhost:8080
```

### 5. Im Browser öffnen
Öffne **http://localhost:8080** in einem beliebigen Browser.

### 6. Testzugänge

| Rolle | E-Mail | Passwort |
|---|---|---|
| Admin | admin@movieticket.ch | admin123 |
| Kunde | wird bei der Registrierung selbst angelegt | – |

### 7. Tickets kaufen
1. Mit einem Kundenkonto einloggen (oder neu registrieren unter `/register`)
2. Auf der Startseite einen Film auswählen
3. Auf **„Tickets kaufen"** klicken
4. Im Kino-Saalplan die gewünschten Sitzplätze anklicken (blau = verfügbar, grün = ausgewählt)
5. Optional: Vergünstigung (Student / Senior / Kind) und Snacks auswählen
6. **„Jetzt bestellen"** klicken
7. Die Bestellübersicht erscheint – PDF-Ticket kann heruntergeladen werden

---

## Tests

### Testmischung
- Insgesamt [Anzahl] Tests: Z.B. 
- Insgesamt [Anzahl] Datenbanktests: Z.B. 
- insgesamt [Anzahl] Integrationstests: Z.B.

### Vorlage zum Erstellen von Testfällen
1. Testfall-ID – eindeutige Kennung (z. B. TC_001)
2. Titel/Beschreibung des Testfalls – Worum geht es in dem Test?
3. Voraussetzungen: Anforderungen vor der Durchführung des Tests
4. Testschritte: Auszuführende Aktionen
5. Testdaten/Eingaben
6. Erwartetes Ergebnis
7. Tatsächliches Ergebnis
8. Status – bestanden oder nicht bestanden
9. Kommentare – Weitere Hinweise oder Mängel festgestellt

## Teammitglieder und Arbeitsaufteilung
| Name | Arbeitsaufteilung |
|---|---|
| Tuana Yildiz | Datenbank, Backend |
| Danijela Djukic | Readme, Backend |
| Medina Senderovic | Frontend, Backend |
  

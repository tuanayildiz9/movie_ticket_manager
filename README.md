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

Im Movie Ticket Manager können Admins:
- Filme hinzufügen, bearbeiten und löschen
- Vorstellungen mit Datum, Uhrzeit und Saal verwalten
- Einsehen, wie viele Tickets pro Film verkauft wurden

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
<img width="643" height="435" alt="Use Case Diagramm" src="https://github.com/user-attachments/assets/5958e561-c00d-49e7-a794-15203bd5d558" />


### Main Use Cases
**Kunde**
- Filme anzeigen
- Filme filtern und sortieren (z. B. nach Kategorie, Sprache)
- Konto anlegen
- Einloggen / Ausloggen
- Tickets kaufen
- Sitzplatz auswählen
- Mehrere Tickets gleichzeitig kaufen
- Rabatte auswählen (Student, Kind, Senior)
- Snacks zum Ticket hinzufügen
- Bestellübersicht anzeigen
- Filme bewerten

**Admin**
- Einloggen / Ausloggen
- Filme hinzufügen
- Filme bearbeiten
- Filme löschen
- Informationen zum Film verwalten (Datum, Uhrzeit, Saal)
- Ticketverkäufe / Verfügbarkeit einsehen (z. B. Anzahl pro Film)
- Übersicht über gebuchte Filme anzeigen

### Rollen
- Kunden (Nutzt die Anwendung zum Suchen, Bewerten und Kaufen von Filmtickets)
- Admin (Mitarbeitende Kino; Verwaltet Inhalte und überwacht das System)

---

## Mockup
<img width="526" height="355" alt="Mockup Anmeldung" src="https://github.com/user-attachments/assets/fcba528c-02b2-4ed5-917e-8b575f7ad637" />


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

## ✅ Projektanforderungen

Jede App muss folgende Kriterien erfüllen, um akzeptiert zu werden:

1. Browserbasierte App mit NiceGUI
2. Datenvalidierung in der App
3. Verwendung eines ORM für die Datenbankverwaltung

### 1. Browserbasierte App (NiceGUI)

Die Anwendung interagiert vollständig über den Browser. NiceGUI stellt die gesamte Benutzeroberfläche als Webanwendung bereit – inklusive:
- Filmübersicht mit Filter- und Sortierfunktionen
- Interaktiver Sitzplan für die Sitzplatzauswahl
- Checkout-Prozess mit Vergünstigungs- und Snack-Auswahl
- Bestellübersicht nach dem Kauf
- Admin-Panel für Film- und Vorstellungsverwaltung

**Architektur-Hinweis:** Der Browser ist ein dünner Client; UI-State und Businesslogik laufen serverseitig in der NiceGUI-App.

### 2. Datenvalidierung

Die Anwendung validiert alle Benutzereingaben, um Datenintegrität und eine fehlerfreie Nutzererfahrung sicherzustellen:
- **Registrierung:** E-Mail, Vorname und Nachname sind Pflichtfelder; doppelte E-Mails werden verhindert
- **Alterscheck:** Kindervergünstigung wird für Filme mit Altersfreigabe ≥ 16 blockiert
- **Sitzplatzbuchung:** Bereits belegte Sitzplätze können nicht erneut reserviert werden
- **Buchungszeitpunkt:** Buchungen für vergangene Vorstellungen werden abgelehnt
- **Bewertung:** Sternebewertung wird auf den Bereich 1–5 eingeschränkt
- **Vorstellungsverwaltung (Admin):** Überschneidungen bei Vorstellungen im gleichen Saal werden verhindert

### 3. Datenbankverwaltung

Alle relevanten Daten werden über ein ORM (SQLModel, basierend auf SQLAlchemy) verwaltet. Dazu gehören:
- Filme, Vorstellungen und Sitzplätze
- Kunden und Accounts (mit getrennter Authentifizierungstabelle)
- Bestellungen und Tickets (inkl. Vergünstigungsart)
- Snacks, Kategorien, Sprachen und Zahlungsarten
- Bewertungen

---

## ⚙️ Implementation

### Technologie

- Python 3.11+
- NiceGUI
- SQLModel / SQLAlchemy
- ReportLab
- pytest

### Verwendete Libraries

| Library | Zweck |
|---|---|
| **nicegui** | Web-UI-Framework (browserbasierte Oberfläche) |
| **sqlmodel** | ORM und Datenbankzugriff (basiert auf SQLAlchemy + Pydantic) |
| **sqlalchemy** | Datenbank-Toolkit (Engine, Sessions, Migrations) |
| **reportlab** | PDF-Ticket-Generierung |
| **pytest** | Testing |

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
├── tests/                           # Automatisierte Tests (pytest)
│   ├── conftest.py                  # Fixtures (In-Memory-DB, Testdaten)
│   ├── test_unit.py                 # 6 Unit Tests (Ticket-Preise, Bestellungstotal)
│   ├── test_db.py                   # 3 Datenbanktests (Repositories)
│   └── test_integration.py          # 3 Integrationstests (BestellungService)
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
- Insgesamt **12** Tests
- Insgesamt **6** Unit Tests: z.B. Ticketpreis regulär, Studentenrabatt, Seniorenrabatt, Kinderrabatt, Mindestpreis 0 CHF, Bestellungstotal
- Insgesamt **3** Datenbanktests: z.B. Filmabfrage mit geseedeten Daten, Bestellung mit Tickets speichern, leere Datenbank
- Insgesamt **3** Integrationstests: z.B. Bestellung mit einem Ticket, Studentenrabatt bei Bestellung, Kinderrabatt bei FSK-16-Film blockiert

Tests ausführen:
```bash
python -m pytest tests/ -v
```

---

### Testfälle

#### Unit Tests

| Feld | TC_001 |
|---|---|
| **Testfall-ID** | TC_001 |
| **Titel** | Regulärer Ticketpreis ohne Rabatt |
| **Voraussetzungen** | `Ticket`-Klasse importierbar, `Verguensigungsart.REGULAER` verfügbar |
| **Testschritte** | Ticket mit REGULAER erstellen → `apply_discount(18.00)` aufrufen |
| **Testdaten** | Basispreis: 18.00 CHF, Vergünstigung: REGULAER |
| **Erwartetes Ergebnis** | Preis = 18.00 CHF (kein Abzug) |
| **Tatsächliches Ergebnis** | 18.00 CHF |
| **Status** | Bestanden |
| **Kommentare** | – |

| Feld | TC_002 |
|---|---|
| **Testfall-ID** | TC_002 |
| **Titel** | Studentenrabatt wird korrekt abgezogen |
| **Voraussetzungen** | `Ticket`-Klasse importierbar |
| **Testschritte** | Ticket mit STUDENT erstellen → `apply_discount(18.00)` aufrufen |
| **Testdaten** | Basispreis: 18.00 CHF, Vergünstigung: STUDENT (−4 CHF) |
| **Erwartetes Ergebnis** | Preis = 14.00 CHF |
| **Tatsächliches Ergebnis** | 14.00 CHF |
| **Status** | Bestanden |
| **Kommentare** | – |

| Feld | TC_003 |
|---|---|
| **Testfall-ID** | TC_003 |
| **Titel** | Seniorenrabatt wird korrekt abgezogen |
| **Voraussetzungen** | `Ticket`-Klasse importierbar |
| **Testschritte** | Ticket mit SENIOR erstellen → `apply_discount(18.00)` aufrufen |
| **Testdaten** | Basispreis: 18.00 CHF, Vergünstigung: SENIOR (−3 CHF) |
| **Erwartetes Ergebnis** | Preis = 15.00 CHF |
| **Tatsächliches Ergebnis** | 15.00 CHF |
| **Status** | Bestanden |
| **Kommentare** | – |

| Feld | TC_004 |
|---|---|
| **Testfall-ID** | TC_004 |
| **Titel** | Kinderrabatt wird korrekt abgezogen |
| **Voraussetzungen** | `Ticket`-Klasse importierbar |
| **Testschritte** | Ticket mit KIND erstellen → `apply_discount(18.00)` aufrufen |
| **Testdaten** | Basispreis: 18.00 CHF, Vergünstigung: KIND (−6 CHF) |
| **Erwartetes Ergebnis** | Preis = 12.00 CHF |
| **Tatsächliches Ergebnis** | 12.00 CHF |
| **Status** | Bestanden |
| **Kommentare** | – |

| Feld | TC_005 |
|---|---|
| **Testfall-ID** | TC_005 |
| **Titel** | Ticketpreis wird nicht negativ bei hohem Rabatt |
| **Voraussetzungen** | `Ticket`-Klasse importierbar |
| **Testschritte** | Ticket mit KIND erstellen → `apply_discount(4.00)` aufrufen |
| **Testdaten** | Basispreis: 4.00 CHF, Vergünstigung: KIND (−6 CHF) |
| **Erwartetes Ergebnis** | Preis = 0.00 CHF (Minimum, kein negativer Preis) |
| **Tatsächliches Ergebnis** | 0.00 CHF |
| **Status** | Bestanden |
| **Kommentare** | – |

| Feld | TC_006 |
|---|---|
| **Testfall-ID** | TC_006 |
| **Titel** | Bestellungssumme aus mehreren Tickets korrekt berechnet |
| **Voraussetzungen** | `Bestellung`- und `Ticket`-Klasse importierbar |
| **Testschritte** | 2 Tickets (REGULAER + STUDENT) erstellen, zur Bestellung hinzufügen, `calculate_total()` aufrufen |
| **Testdaten** | Ticket 1: 18.00 CHF (regulär), Ticket 2: 14.00 CHF (student) |
| **Erwartetes Ergebnis** | Total = 32.00 CHF |
| **Tatsächliches Ergebnis** | 32.00 CHF |
| **Status** | Bestanden |
| **Kommentare** | – |

---

#### Datenbanktests

| Feld | TC_007 |
|---|---|
| **Testfall-ID** | TC_007 |
| **Titel** | Filmabfrage liefert alle geseedeten Filme |
| **Voraussetzungen** | In-Memory-SQLite-DB, 2 Filme eingetragen (Inception FSK 12, Matrix FSK 16) |
| **Testschritte** | `film_repo.list_all()` aufrufen |
| **Testdaten** | Film 1: „Inception" (18 CHF), Film 2: „Matrix" (20 CHF) |
| **Erwartetes Ergebnis** | Liste mit 2 Filmen; Titel „Inception" und „Matrix" enthalten |
| **Tatsächliches Ergebnis** | 2 Filme, beide Titel vorhanden |
| **Status** | Bestanden |
| **Kommentare** | – |

| Feld | TC_008 |
|---|---|
| **Testfall-ID** | TC_008 |
| **Titel** | Gespeicherte Bestellung ist mit Tickets wiederabrufbar |
| **Voraussetzungen** | In-Memory-DB, Film + Vorstellung + Sitzplatz vorhanden |
| **Testschritte** | Ticket erstellen → Bestellung anlegen → `bestellung_repo.create()` → `get_by_id()` |
| **Testdaten** | 1 Ticket (REGULAER, 18.00 CHF), zufällige Kunden-UUID |
| **Erwartetes Ergebnis** | Geladene Bestellung hat 1 Ticket, `total_betrag` = 18.00 CHF |
| **Tatsächliches Ergebnis** | 1 Ticket, 18.00 CHF |
| **Status** | Bestanden |
| **Kommentare** | – |

| Feld | TC_009 |
|---|---|
| **Testfall-ID** | TC_009 |
| **Titel** | Leere Datenbank liefert leere Filmliste |
| **Voraussetzungen** | Frische In-Memory-DB ohne eingetragene Filme |
| **Testschritte** | `film_repo.list_all()` auf leerer DB aufrufen |
| **Testdaten** | Keine |
| **Erwartetes Ergebnis** | Leere Liste `[]` |
| **Tatsächliches Ergebnis** | `[]` |
| **Status** | Bestanden |
| **Kommentare** | – |

---

#### Integrationstests

| Feld | TC_010 |
|---|---|
| **Testfall-ID** | TC_010 |
| **Titel** | Bestellung mit einem Ticket wird korrekt erstellt |
| **Voraussetzungen** | In-Memory-DB, Film + Vorstellung + Sitzplatz + Kunde vorhanden |
| **Testschritte** | `BestellungService.create_order()` mit 1 regulärem Ticket aufrufen |
| **Testdaten** | Film: Inception (18 CHF), Vergünstigung: REGULAER |
| **Erwartetes Ergebnis** | Bestellung mit ID, `anzahl_tickets` = 1, `total_betrag` = 18.00 CHF |
| **Tatsächliches Ergebnis** | Bestellung erstellt, 18.00 CHF |
| **Status** | Bestanden |
| **Kommentare** | – |

| Feld | TC_011 |
|---|---|
| **Testfall-ID** | TC_011 |
| **Titel** | Studentenrabatt wird bei Bestellung korrekt verrechnet |
| **Voraussetzungen** | In-Memory-DB, Film mit 2 Sitzplätzen + Kunde vorhanden |
| **Testschritte** | `create_order()` mit 2 Tickets aufrufen (1× STUDENT, 1× REGULAER) |
| **Testdaten** | Basispreis: 18 CHF; Ticket 1: STUDENT (14 CHF), Ticket 2: REGULAER (18 CHF) |
| **Erwartetes Ergebnis** | `anzahl_tickets` = 2, `total_betrag` = 32.00 CHF |
| **Tatsächliches Ergebnis** | 2 Tickets, 32.00 CHF |
| **Status** | Bestanden |
| **Kommentare** | – |

| Feld | TC_012 |
|---|---|
| **Testfall-ID** | TC_012 |
| **Titel** | Kinderrabatt bei FSK-16-Film wird blockiert |
| **Voraussetzungen** | In-Memory-DB, Film mit `altersfreigabe=16` + Kunde vorhanden |
| **Testschritte** | `create_order()` mit Vergünstigung KIND für FSK-16-Film aufrufen |
| **Testdaten** | Film: Matrix (FSK 16, 20 CHF), Vergünstigung: KIND |
| **Erwartetes Ergebnis** | `ValueError` mit Meldung „Kindervergünstigung" |
| **Tatsächliches Ergebnis** | `ValueError` ausgelöst |
| **Status** | Bestanden |
| **Kommentare** | Geschäftsregel korrekt durchgesetzt |

---

## Teammitglieder und Arbeitsaufteilung
| Name | Arbeitsaufteilung |
|---|---|
| Tuana Yildiz | Datenbank, Backend |
| Danijela Djukic | Readme, Backend |
| Medina Senderovic | Frontend, Backend |

---

## Lizenz

Dieses Projekt wurde für **Bildungszwecke** erstellt im Rahmen des Moduls Advanced Programming.

[MIT License](LICENSE)


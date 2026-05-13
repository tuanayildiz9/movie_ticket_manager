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
| ID | User Story | Priorität | Status | Input | Input-Typ | Output | Output-Typ |
|---|---|---|---|---|---|---|---|
| US-01 | Als Kunde möchte ich die aktuellen Filme sehen, damit ich informiert Tickets kaufen kann. | Hoch | Umgesetzt | – | – | Filmliste (Titel, Bild, Kategorie, Sprache) | List[Film] |
| US-02 | Als Kunde möchte ich ein Konto anlegen können, damit ich all meine Käufe einfach verwalten kann. | Hoch | Umgesetzt | Vorname, Nachname, E-Mail, Passwort, Geburtsdatum, Adresse, Zahlungsart | String, String, String, String, Date, String, String | Kontobestätigung | Boolean |
| US-03 | Als Kunde möchte ich Tickets kaufen können, damit ich die Tickets bequem im Voraus besorgen kann und mir den Zugang ins Kino vereinfachen kann. | Hoch | Umgesetzt | Film-ID, Vorstellungs-ID, Anzahl Tickets, Zahlungsart | Int, Int, Int, String | Bestellbestätigung, Bestellübersicht | Boolean, String |
| US-04 | Als Kunde möchte ich Sitzplätze auswählen können, damit ich entscheiden kann, wo ich sitze. | Hoch | Umgesetzt | Vorstellungs-ID, Sitzplatz | Int, String | Bestätigter Sitzplatz, Sitzplatz als belegt markiert | String, Boolean |
| US-05 | Als Kunde möchte ich die Filme auf der Webseite sortieren und filtern können, da ich damit meine Suche nach Filmen verfeinern kann. | Mittel | Umgesetzt | Filteroptionen (Kategorie, Sprache, Altersfreigabe) | String, String, Int | Gefilterte Filmliste | List[Film] |
| US-06 | Als Kunde möchte ich Rabatte (Student, Senior, Kind) auswählen können, damit ich den vergünstigten Preis erhalte. | Mittel | Umgesetzt | Rabatt-Typ | String | Aktualisierter Ticketpreis | Float |
| US-07 | Als Kunde möchte ich Snacks zum Ticket hinzufügen können, damit ich mein Kinoerlebnis bequem planen kann. | Niedrig | Umgesetzt | Snack-Auswahl | String | Snack zum Ticket hinzugefügt, Gesamtpreis aktualisiert | Boolean, Float |
| US-08 | Als Kunde möchte ich nach dem Kauf eine Bestellübersicht sehen, damit ich alle Details meines Tickets auf einen Blick habe. | Hoch | Umgesetzt | – | – | Filmtitel, Saal, Sitzplatz, Datum, Uhrzeit, Anzahl Tickets, Gesamtpreis | String, String, String, Date, Time, Int, Float |
| US-09 | Als Kunde möchte ich Filme bewerten können, damit ich meine Meinung teilen kann. | Niedrig | Umgesetzt | Sternebewertung, Kommentar | Int, String | Gespeicherte Bewertung | Boolean |

### Admin
| ID | User Story | Priorität | Status | Input | Input-Typ | Output | Output-Typ |
|---|---|---|---|---|---|---|---|
| AS-01 | Als Admin möchte ich neue Filme hinzufügen können, damit das Filmprogramm aktuell angezeigt wird. | Hoch | Offen | Titel, Beschreibung, Kategorie, Sprache, Altersfreigabe, Coverbild, Erscheinungsjahr | String, String, String, String, Int, String, Int | Neuer Film in der Datenbank | Boolean |
| AS-02a | Als Admin möchte ich bestehende Filme bearbeiten können, damit falsche Informationen korrigiert werden können. | Hoch | Offen | Film-ID, Titel, Beschreibung, Kategorie, Sprache, Altersfreigabe, Coverbild, Erscheinungsjahr | Int, String, String, String, String, Int, String, Int | Aktualisierter Film in der Datenbank | Boolean |
| AS-02b | Als Admin möchte ich Filme löschen können, damit veraltete Einträge entfernt werden. | Hoch | Offen | Film-ID | Int | Film aus der Datenbank gelöscht | Boolean |

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
(Bild)

### Schichten


### Designentscheidung

### Verwendete Designmuster

---

## Datenbank und ORM

### Einheiten
- Tickets
- Filme
- Sitzplätze
  
### Beziehungen

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

(Verlinkung)

## How-to Programm starten
1. Projektaufbau
- Python 3.13 (oder Kursversion) ist Pflicht
- Erstelle und aktiviere eine virutelle Umgebung:
  - macOS/Linux:
  
  - Windows:

       
- Installationsabhängigkeit:


2. Konfiguration???
- Zum Beispiel die Einrichtung von Parametern oder Umwelt

3. Start
- Starte die NiceGui-App (Beispiel):


- Öffnen Sie die in der Konsole sausgedruckte URL

4. Verwendung (Dokumentiert als Schritte)
Beschreibung der Verwendung der Hauptfunktion

Tickets kaufen:
1. text...
2. text...

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
  
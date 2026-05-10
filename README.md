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
- Admins können einsehen, wie viele Tickets pro Film verkauft wurden und welche Sitzplätze belegt sind


## User-Stories
### Kunde
|ID |User Story |Priorität|Status |
|---|:---:      |:----    |:----: |
|US01|Als Kunde möchte ich die Filme sehen, welche im Kino aktuell laufen. | hoch | offen |

|ID |User Story |Priorität|Status |
|---|:---:      |:----    |:----: |
|US02|Als Kunde möchte ich ein Konto anlegen können, damit ich all meine Käufe einfach verwalten kann. | hoch | offen |

|ID |User Story |Priorität|Status |
|---|:---:      |:----    |:----: |
|US03|Als Kunde möchte ich Tickets kaufen können, damit ich die Tickets bequem im Voraus besorgen kann und mir den Zugang ins Kino vereinfachen kann. | hoch | offen |

|ID |User Story |Priorität|Status |
|---|:---:      |:----    |:----: |
|US04|Als Kunde möchte ich die Möglichkeit haben, die Sitzplätze auswählen zu können, damit ich entscheiden kann, wi ich hinsitzen möchte. | hoch | offen |

|ID |User Story |Priorität|Status |
|---|:---:      |:----    |:----: |
|US05|Als Kunde möchte ich die Filme auf der Webseite sortieren und filtern können, da ich damit meine Suche nach Filmen verfeinern kann. | medium | offen |

### Admin
|ID |User Story |Priorität|Status |
|---|:---:      |:----    |:----: |
|AS01|Als Admin möchte ich sehen können, vie viel Ticktes für einen Film gekauft wurden, bzw. wie viel Sitzplätze noch frei sind. Somit kann ich bin ich über den Stand des Ticktesverkauf stehts informiert und kann den Kunden eine Auskunft darüber geben. | hoch | offen |

## Use Cases
(Diagramm)

### Main Use Cases
- Filme anzeigen (Kunde)
- Konto anlegen (Kunde)
- Kinotickets kaufen (Kunde)
- Anzeige frei/gekaufte Kinotickets (Admin)

### Rollen
- Kunden
- Admin (Mitarbeitende Kino)

## Funktionsübersicht
Die Anwendung bietet folgende Funktionen:
1. Aktuelle Filme, welche im Kino laufen, werden angezeigt.
- Titel
- Beschreibung
- Altersfreigabe
- Coverbild
- Hauptdarsteller
- Erscheinungsjahr/datum
- Kategorie (Comedy, Romance, Sci-Fi, Phantasy)
- Sprache (In welcher Sprache der Film im Kino verfügbar ist)
2. Kunden können ein Konto anlegen
- Name
- Nachname
- Adresse
- PLZ
- Geburtsdatum
- Alter (wird vom Geburtsdatum berechnet, der Kunde muss nur sein Geburtsdatum eingeben beim Anlegen eines Kontos)
- Telefonnummer
- E-Mail
- Passwort
- Zahlungsart (Karte, Rechnung, TWINT)
- Präferenzen Kategorie
- Filmliste
3. Kunden können Tickets kaufen
- Es können mehrere Tickets gekauft werden
- Es gibt Senioren-, Studenten- und Kindervergünstigung
4. Zu den Tickets können Snacks mitgebucht werden
5. Man kann seinen Sitzplatz selbst auswählen
- Sektor A, B, C (anstatt 21C auswählen, falls UI nicht vorhanden)
- Dropdown
- Array
6. Beim Kauf eines Tickets wird jedem Kunden ein Sitzplatz zugeteilt. 
7. Admins können (MA im Kino) sehen, wie viele Personen sich Tickets für dieses Film gekauft haben
8. Kunden können Filme bewerten
9. Kunden können Filme in ihrer Liste speichern
10. Kunden können filtern (Sprache, Kategorie, Altersfreigabe)
11. Das System erstellt eine Bestellungsübersicht, nachdem der Kunde ein Ticket gekauft hat mit folgenden Informationen:
  - Saal
  -	Ort
  -	Uhrzeit
  -	Anzahl Tickets
  -	Filmtitel

## Architektur
(Bild)

### Schichten


### Designentscheidung

### Verwendete Designmuster


## Datenbank und ORM

### Einheiten
- Tickets
- Filme
- Sitzplätze
  
### Beziehungen


## Datentypen
|Feldname |Beschreibung |Datentyp |Pflichtfeld |Beispeil |
|---      |:---:        |:----    |:----:      |:----    |
|Titel    |Der Titel vom Film |String |Ja |"Titanic"|

## Inputs

### Eingabedaten
- Welche Daten werden benötigt?
- Herkunft der Daten
- Format der Daten

### Eingabemethoden
- Manuelle Eingabe

### Erwartetes Format
|Output |Beschreibung |Format |Empfänger |
|---    |:---:        |:----  |:----:    |
|text |text | text | text |

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
|Name |Arbeitsaufteilung |
|---    |:---            |
|Tuana Yildiz| Datenbank, Backend|
|Danijela Djukic| Readme, Backend|
|Medina Senderovic| Frontend, Backend|
  

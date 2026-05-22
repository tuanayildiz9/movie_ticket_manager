"""PDF-Ticket-Generierung mit reportlab."""
from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Kino-Farbpalette
AMBER      = colors.HexColor("#F59E0B")
DARK       = colors.HexColor("#1F2937")
GRAY       = colors.HexColor("#6B7280")
WHITE      = colors.white
LIGHT_GRAY = colors.HexColor("#F3F4F6")


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title", parent=base["Title"],
            fontSize=24, textColor=AMBER, spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"],
            fontSize=10, textColor=GRAY, spaceAfter=12,
        ),
        "section": ParagraphStyle(
            "section", parent=base["Normal"],
            fontSize=12, textColor=DARK,
            fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4,
        ),
        "normal": ParagraphStyle(
            "normal", parent=base["Normal"],
            fontSize=10, textColor=DARK,
        ),
        "small": ParagraphStyle(
            "small", parent=base["Normal"],
            fontSize=8, textColor=GRAY,
        ),
        "total": ParagraphStyle(
            "total", parent=base["Normal"],
            fontSize=14, fontName="Helvetica-Bold", textColor=AMBER,
        ),
    }


def generate_ticket_pdf(
    bestellung,
    snacks_map: dict,
    film_vorstellung_map: dict,
    sitzplatz_map: dict,
) -> bytes:
    """
    Generiert ein PDF-Ticket.

    Parameters
    ----------
    bestellung           : Bestellung-Domain-Objekt
    snacks_map           : {snack_id: Snack-ORM-Objekt}
    film_vorstellung_map : {vorstellung_id: {"titel", "startzeit", "ort", "saal"}}
    sitzplatz_map        : {sitzplatz_id: {"sektor", "sitz_label"}}
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm,  bottomMargin=2 * cm,
    )
    s = _styles()
    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph("🎬 MovieTicket", s["title"]))
    story.append(Paragraph("Ihr offizielles Kinoticket", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=AMBER, spaceAfter=12))

    # ── Bestellinfo ─────────────────────────────────────────────────────────
    bid_short = str(bestellung.bestellung_id)[:8].upper()
    datum = bestellung.bestellungsdatum.strftime("%d.%m.%Y")
    meta_data = [
        ["Bestellnummer:", bid_short],
        ["Bestelldatum:",  datum],
        ["Anzahl Tickets:", str(bestellung.anzahl_tickets)],
    ]
    meta_table = Table(meta_data, colWidths=[5 * cm, 11 * cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",     (0, 0), (0, -1), DARK),
        ("TEXTCOLOR",     (1, 0), (1, -1), GRAY),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.4 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY, spaceAfter=8))

    # ── Tickets ─────────────────────────────────────────────────────────────
    story.append(Paragraph("Tickets", s["section"]))

    discount_labels = {
        "regulaer": "Regulär",
        "student":  "Student (−CHF 4.00)",
        "senior":   "Senior (−CHF 3.00)",
        "kind":     "Kind (−CHF 6.00)",
    }

    for i, ticket in enumerate(bestellung.tickets, 1):
        fv   = film_vorstellung_map.get(ticket.vorstellung_id, {})
        sitz = sitzplatz_map.get(ticket.sitzplatz_id, {})
        disc_key   = ticket.verguenstigungsart.value if hasattr(ticket.verguenstigungsart, "value") else str(ticket.verguenstigungsart)
        disc_label = discount_labels.get(disc_key, disc_key.capitalize())

        startzeit_str = fv.get("startzeit")
        if startzeit_str and hasattr(startzeit_str, "strftime"):
            startzeit_str = startzeit_str.strftime("%d.%m.%Y %H:%M")
        else:
            startzeit_str = "–"

        ticket_rows = [
            [Paragraph(f"Ticket {i}", s["section"]), ""],
            ["Film:",           fv.get("titel", "–")],
            ["Datum / Uhrzeit:", startzeit_str],
            ["Ort / Saal:",     f"{fv.get('ort', '–')} · {fv.get('saal', '–')}"],
            ["Sitzplatz:",      f"Reihe {sitz.get('sektor', '–')}, Platz {sitz.get('sitz_label', '–').lstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') or sitz.get('sitz_label', '–')}"],
            ["Vergünstigung:",  disc_label],
            ["Ticketpreis:",    f"CHF {ticket.preis:.2f}"],
        ]

        t = Table(ticket_rows, colWidths=[5 * cm, 11 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), LIGHT_GRAY),
            ("SPAN",         (0, 0), (-1, 0)),
            ("FONTNAME",     (0, 1), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, -1), 10),
            ("TEXTCOLOR",    (0, 1), (0, -1), DARK),
            ("TEXTCOLOR",    (1, 1), (1, -1), GRAY),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOX",          (0, 0), (-1, -1), 0.5, GRAY),
            ("INNERGRID",    (0, 0), (-1, -1), 0.25, LIGHT_GRAY),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3 * cm))

    # ── Snack-Tabelle (NACH allen Tickets, aggregiert) ───────────────────────
    all_snack_lines: dict = {}   # snack_id → (snack, total_anzahl)
    for ticket in bestellung.tickets:
        for ts in ticket.snacks:
            if ts.snack_id in snacks_map:
                snack = snacks_map[ts.snack_id]
                if ts.snack_id in all_snack_lines:
                    all_snack_lines[ts.snack_id] = (snack, all_snack_lines[ts.snack_id][1] + ts.anzahl)
                else:
                    all_snack_lines[ts.snack_id] = (snack, ts.anzahl)

    if all_snack_lines:
        story.append(Paragraph("Snacks", s["section"]))
        snack_header = [["Snack", "Preis", "Anzahl", "Total"]]
        snack_data = [
            [
                snack.name,
                f"CHF {snack.preis:.2f}",
                str(anzahl),
                f"CHF {snack.preis * anzahl:.2f}",
            ]
            for snack, anzahl in all_snack_lines.values()
        ]
        snack_table = Table(
            snack_header + snack_data,
            colWidths=[7 * cm, 3 * cm, 2 * cm, 4 * cm],
        )
        snack_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), LIGHT_GRAY),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 10),
            ("TEXTCOLOR",     (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR",     (0, 1), (-1, -1), GRAY),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            ("BOX",           (0, 0), (-1, -1), 0.5, GRAY),
            ("INNERGRID",     (0, 0), (-1, -1), 0.25, LIGHT_GRAY),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ]))
        story.append(snack_table)
        story.append(Spacer(1, 0.3 * cm))

    # ── Gesamtbetrag ────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=AMBER, spaceBefore=8, spaceAfter=8))
    total_data = [["Gesamtbetrag:", f"CHF {bestellung.total_betrag:.2f}"]]
    total_table = Table(total_data, colWidths=[5 * cm, 11 * cm])
    total_table.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",  (0, 0), (-1, -1), 13),
        ("TEXTCOLOR", (0, 0), (0, 0), DARK),
        ("TEXTCOLOR", (1, 0), (1, 0), AMBER),
    ]))
    story.append(total_table)

    # ── Footer ──────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY, spaceAfter=6))
    story.append(Paragraph("Bitte zeigen Sie dieses Ticket beim Einlass vor. Viel Spass im Kino!", s["small"]))
    story.append(Paragraph(f"MovieTicket · Bestellung {bid_short}", s["small"]))

    doc.build(story)
    return buffer.getvalue()

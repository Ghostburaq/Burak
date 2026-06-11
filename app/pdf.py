"""PDF-Erzeugung fuer Angebote und Mietvertraege mit reportlab."""
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT

from .logic import line_total, calc_event

BRAND = colors.HexColor("#0e7490")
LIGHT = colors.HexColor("#ecfeff")
GREY = colors.HexColor("#64748b")


def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("Small", parent=s["Normal"], fontSize=8, textColor=GREY))
    s.add(ParagraphStyle("RightSmall", parent=s["Normal"], fontSize=8, alignment=TA_RIGHT, textColor=GREY))
    s.add(ParagraphStyle("H1b", parent=s["Heading1"], textColor=BRAND, fontSize=18))
    s.add(ParagraphStyle("Cell", parent=s["Normal"], fontSize=9))
    s.add(ParagraphStyle("CellR", parent=s["Normal"], fontSize=9, alignment=TA_RIGHT))
    s.add(ParagraphStyle("CellB", parent=s["Normal"], fontSize=9, fontName="Helvetica-Bold"))
    return s


def _eur(v):
    return f"{v:,.2f} EUR".replace(",", "X").replace(".", ",").replace("X", ".")


RATE_LABEL = {"daily": "Tagesmiete", "weekend": "Wochenende", "weekly": "Wochenmiete", "fixed": "Pauschale"}


def build_document(settings, customer, event, items, doc_type="Angebot"):
    """Erzeugt ein PDF (bytes) fuer Angebot oder Mietvertrag."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm, title=f"{doc_type} {event['title']}",
    )
    s = _styles()
    el = []

    # Kopf: Firma + Dokumenttitel
    company = settings["company_name"] or "Firma"
    head = Table(
        [[Paragraph(f"<b>{company}</b><br/>{settings['address'] or ''}<br/>"
                    f"{settings['phone'] or ''} &middot; {settings['email'] or ''}", s["Small"]),
          Paragraph(f"{doc_type}", s["H1b"])]],
        colWidths=[110 * mm, 64 * mm],
    )
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                              ("ALIGN", (1, 0), (1, 0), "RIGHT")]))
    el.append(head)
    el.append(Spacer(1, 8 * mm))

    # Empfaenger + Meta
    cust_block = "Kein Kunde zugeordnet"
    if customer:
        cust_block = (f"<b>{customer['company']}</b><br/>{customer['contact'] or ''}<br/>"
                      f"{customer['street'] or ''}<br/>{customer['zip'] or ''} {customer['city'] or ''}")
    meta = (f"<b>{doc_type}-Nr.:</b> {doc_type[:1]}-{event['id']:04d}<br/>"
            f"<b>Event:</b> {event['title']}<br/>"
            f"<b>Zeitraum:</b> {event['start_date'] or '-'} bis {event['end_date'] or '-'}<br/>"
            f"<b>Ort:</b> {event['location'] or '-'}")
    addr = Table([[Paragraph(cust_block, s["Cell"]), Paragraph(meta, s["Cell"])]],
                 colWidths=[90 * mm, 84 * mm])
    addr.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    el.append(addr)
    el.append(Spacer(1, 6 * mm))

    if event["description"]:
        el.append(Paragraph(event["description"], s["Cell"]))
        el.append(Spacer(1, 5 * mm))

    # Positionstabelle
    header = ["Pos", "Beschreibung", "Menge", "Tarif", "Tage", "Einzelpreis", "Summe"]
    data = [header]
    for idx, it in enumerate(items, 1):
        data.append([
            str(idx),
            Paragraph(it["description"] or it["name"] or "-", s["Cell"]),
            f"{float(it['quantity']):g}",
            RATE_LABEL.get(it["rate_type"], it["rate_type"]),
            f"{float(it['days']):g}" if it["rate_type"] in ("daily", "weekly") else "-",
            _eur(float(it["unit_price"])),
            _eur(line_total(it)),
        ])
    tbl = Table(data, colWidths=[10 * mm, 64 * mm, 14 * mm, 22 * mm, 12 * mm, 26 * mm, 26 * mm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, BRAND),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    el.append(tbl)
    el.append(Spacer(1, 5 * mm))

    # Summen
    calc = calc_event(event, items, settings["vat_rate"] or 19)
    rows = [["Zwischensumme", _eur(calc["subtotal"])]]
    if calc["discount_amount"]:
        rows.append([f"Rabatt {calc['discount_pct']:g}%", "-" + _eur(calc["discount_amount"])])
    if calc["service_fee"]:
        rows.append(["Servicegebuehr", _eur(calc["service_fee"])])
    rows.append(["Nettobetrag", _eur(calc["net"])])
    rows.append([f"MwSt. {calc['vat_rate']:g}%", _eur(calc["vat"])])
    rows.append(["Gesamtbetrag", _eur(calc["gross"])])
    if calc["deposit"]:
        rows.append(["Kaution (separat)", _eur(calc["deposit"])])

    sums = Table(rows, colWidths=[44 * mm, 36 * mm], hAlign="RIGHT")
    style = [
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    gross_row = len(rows) - 2 if calc["deposit"] else len(rows) - 1
    style += [
        ("LINEABOVE", (0, gross_row), (-1, gross_row), 0.7, BRAND),
        ("FONTNAME", (0, gross_row), (-1, gross_row), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, gross_row), (-1, gross_row), BRAND),
    ]
    sums.setStyle(TableStyle(style))
    el.append(sums)
    el.append(Spacer(1, 8 * mm))

    if doc_type == "Mietvertrag":
        el.append(Paragraph(
            "Der Mieter bestaetigt den Erhalt des Mietgegenstands in einwandfreiem Zustand. "
            "Die Kaution wird nach Rueckgabe und Pruefung erstattet. Kraftstoff wird nach Verbrauch abgerechnet.",
            s["Small"]))
        el.append(Spacer(1, 14 * mm))
        sign = Table([[Paragraph("_______________________<br/>Vermieter", s["Small"]),
                       Paragraph("_______________________<br/>Mieter", s["Small"])]],
                     colWidths=[80 * mm, 80 * mm])
        el.append(sign)
        el.append(Spacer(1, 6 * mm))

    el.append(Paragraph(settings["footer"] or "", s["Small"]))
    if settings["iban"]:
        el.append(Paragraph(f"Bank: {settings['bank'] or ''} &middot; IBAN: {settings['iban']} &middot; "
                            f"USt-IdNr.: {settings['tax_id'] or ''}", s["Small"]))

    doc.build(el)
    buf.seek(0)
    return buf.read()

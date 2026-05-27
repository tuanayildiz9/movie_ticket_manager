from decimal import Decimal

from backend.models import Bestellung, Ticket, Verguensigungsart


def test_ticket_preis_regulaer():
    ticket = Ticket(verguenstigungsart=Verguensigungsart.REGULAER)
    assert ticket.apply_discount(Decimal("18.00")) == Decimal("18.00")


def test_ticket_discount_student():
    ticket = Ticket(verguenstigungsart=Verguensigungsart.STUDENT)
    assert ticket.apply_discount(Decimal("18.00")) == Decimal("14.00")


def test_ticket_discount_senior():
    ticket = Ticket(verguenstigungsart=Verguensigungsart.SENIOR)
    assert ticket.apply_discount(Decimal("18.00")) == Decimal("15.00")


def test_ticket_discount_kind():
    ticket = Ticket(verguenstigungsart=Verguensigungsart.KIND)
    assert ticket.apply_discount(Decimal("18.00")) == Decimal("12.00")


def test_ticket_discount_minimum_zero():
    # KIND discount is 6 CHF; base price of 4 CHF must not go below 0
    ticket = Ticket(verguenstigungsart=Verguensigungsart.KIND)
    assert ticket.apply_discount(Decimal("4.00")) == Decimal("0.00")


def test_bestellung_total_multiple_tickets():
    bestellung = Bestellung()
    t1 = Ticket(verguenstigungsart=Verguensigungsart.REGULAER)
    t1.apply_discount(Decimal("18.00"))   # 18.00
    t2 = Ticket(verguenstigungsart=Verguensigungsart.STUDENT)
    t2.apply_discount(Decimal("18.00"))   # 14.00
    bestellung.add_ticket(t1)
    bestellung.add_ticket(t2)
    assert bestellung.calculate_total() == Decimal("32.00")

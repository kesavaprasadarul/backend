# generated by datamodel-codegen:
#   filename:  openapi_dip.yaml
#   timestamp: 2023-11-22T12:11:21+00:00

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel


class ListResponseBase(BaseModel):
    numFound: int = Field(
        ...,
    )
    cursor: str = Field(
        ...,
    )


class VorgangTyp(Enum):
    Vorgang = 'Vorgang'


class VorgangspositionTyp(Enum):
    Vorgangsposition = 'Vorgangsposition'


class DokumentTyp(Enum):
    Dokument = 'Dokument'


class AktivitaetTyp(Enum):
    Aktivitaet = 'Aktivität'


class Dokumentart(Enum):
    Drucksache = 'Drucksache'
    Plenarprotokoll = 'Plenarprotokoll'


class DokumentartDrucksache(Enum):
    Drucksache = 'Drucksache'


class Herausgeber(Enum):
    BT = 'BT'
    BR = 'BR'


class AutorenAnzeigeItem(BaseModel):
    id: int = Field(
        ...,
        description='ID von Personenstammdaten',
    )
    titel: str = Field(
        ...,
    )
    autor_titel: str = Field(
        ...,
    )


class DokumentartPlenarprotokoll(Enum):
    Plenarprotokoll = 'Plenarprotokoll'


class DokumentTextBase(BaseModel):
    text: Optional[str] = Field(
        None,
        description='Volltext des Dokuments\n\nDas Beispiel enthält einen gekürzten Auszug einer Drucksache.\n',
    )


class AktivitaetAnzeige(BaseModel):
    aktivitaetsart: str = Field(
        ...,
    )
    titel: str = Field(
        ...,
    )
    pdf_url: Optional[str] = Field(
        None,
    )
    seite: Optional[str] = Field(
        None,
    )


class Abstimmungsart(Enum):
    Abstimmung_durch_Aufruf_der_Länder = 'Abstimmung durch Aufruf der Länder'
    Geheime_Wahl = 'Geheime Wahl'
    Hammelsprung = 'Hammelsprung'
    Namentliche_Abstimmung = 'Namentliche Abstimmung'
    Verhältniswahl = 'Verhältniswahl'


class Mehrheit(Enum):
    Absolute_Mehrheit = 'Absolute Mehrheit'
    Zweidrittelmehrheit = 'Zweidrittelmehrheit'


class Beschlussfassung(BaseModel):
    beschlusstenor: str = Field(
        ...,
    )
    seite: Optional[str] = Field(
        None,
    )
    abstimmungsart: Optional[Abstimmungsart] = None
    abstimm_ergebnis_bemerkung: Optional[str] = Field(
        None,
    )
    grundlage: Optional[str] = Field(
        None,
    )
    dokumentnummer: Optional[str] = Field(
        None,
    )
    mehrheit: Optional[Mehrheit] = None


class VorgangDeskriptorTyp(Enum):
    Freier_Deskriptor = 'Freier Deskriptor'
    Geograph_Begriffe = 'Geograph. Begriffe'
    Institutionen = 'Institutionen'
    Personen = 'Personen'
    Rechtsmaterialien = 'Rechtsmaterialien'
    Sachbegriffe = 'Sachbegriffe'


class Deskriptor(BaseModel):
    name: str = Field(
        ...,
    )
    typ: VorgangDeskriptorTyp = Field(
        ...,
    )


class Inkrafttreten(BaseModel):
    datum: date = Field(
        ...,
    )
    erlaeuterung: Optional[str] = Field(
        None,
    )


class Ressort(BaseModel):
    federfuehrend: bool = Field(
        ...,
    )
    titel: str = Field(
        ...,
    )


class Ueberweisung(BaseModel):
    ausschuss: str = Field(
        ...,
    )
    ausschuss_kuerzel: str = Field(
        ...,
    )
    federfuehrung: bool = Field(
        ...,
    )
    ueberweisungsart: Optional[str] = Field(
        None,
    )


class Rolle(Enum):
    B = 'B'
    U = 'U'


class Urheber(BaseModel):
    einbringer: Optional[bool] = None
    bezeichnung: str = Field(
        ...,
    )
    titel: str = Field(
        ...,
    )
    rolle: Optional[Rolle] = None


class Verkuendung(BaseModel):
    jahrgang: Optional[str] = Field(
        None,
    )
    heftnummer: Optional[str] = Field(
        None,
    )
    seite: Optional[str] = Field(
        None,
    )
    ausfertigungsdatum: date = Field(
        ...,
    )
    verkuendungsdatum: date = Field(
        ...,
    )
    rubrik_nr: Optional[str] = Field(
        None,
    )
    einleitungstext: str = Field(None)
    verkuendungsblatt_bezeichnung: Optional[str] = Field(
        None,
    )
    verkuendungsblatt_kuerzel: Optional[str] = Field(
        None,
    )
    fundstelle: str = Field(
        ...,
    )
    pdf_url: Optional[str] = Field(
        None,
    )
    titel: Optional[str] = Field(
        None,
    )


class VorgangDeskriptor(Deskriptor):
    fundstelle: bool = Field(
        ...,
        description='Kennzeichnet Deskriptoren mit zentraler Bedeutung',
    )


class Vorgangsbezug(BaseModel):
    id: int = Field(..., description='ID eines verknüpften Vorgangs')
    titel: str = Field(
        ...,
    )
    vorgangstyp: str = Field(
        ...,
    )


class Vorgangspositionbezug(Vorgangsbezug):
    vorgangsposition: str = Field(
        ...,
    )


class VorgangVerlinkung(BaseModel):
    id: int = Field(..., description='ID eines verknüpften Vorgangs')
    verweisung: str = Field(
        ...,
    )
    titel: str = Field(
        ...,
    )
    wahlperiode: int = Field(
        ...,
    )
    gesta: Optional[str] = None


class Bundesland(Enum):
    Baden_Württemberg = 'Baden-Württemberg'
    Bayern = 'Bayern'
    Berlin = 'Berlin'
    Brandenburg = 'Brandenburg'
    Bremen = 'Bremen'
    Hamburg = 'Hamburg'
    Hessen = 'Hessen'
    Mecklenburg_Vorpommern = 'Mecklenburg-Vorpommern'
    Niedersachsen = 'Niedersachsen'
    Nordrhein_Westfalen = 'Nordrhein-Westfalen'
    Rheinland_Pfalz = 'Rheinland-Pfalz'
    Saarland = 'Saarland'
    Sachsen = 'Sachsen'
    Sachsen_Anhalt = 'Sachsen-Anhalt'
    Schleswig_Holstein = 'Schleswig-Holstein'
    Thüringen = 'Thüringen'


class Datum(RootModel):
    root: date = Field(
        ..., description='Liefert das Datum eines Dokuments (Drucksache oder Protokoll).'
    )


class Quadrant(Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'


class Zuordnung(Enum):
    BT = 'BT'
    BR = 'BR'
    BV = 'BV'
    EK = 'EK'


class Vorgang(BaseModel):
    id: int = Field(
        ...,
    )
    typ: VorgangTyp = Field(
        ...,
    )
    beratungsstand: Optional[str] = Field(
        None,
    )
    vorgangstyp: str = Field(
        ...,
    )
    wahlperiode: int = Field(
        ...,
    )
    initiative: Optional[List[str]] = None
    datum: Optional[date] = Field(
        None,
        description='Datierung des letzten zugehörigen Dokuments',
    )
    aktualisiert: datetime = Field(
        ...,
        description='Letzte Aktualisierung der Entität',
    )
    titel: str = Field(
        ...,
    )
    abstract: Optional[str] = Field(
        None,
    )
    sachgebiet: Optional[List[str]] = None
    deskriptor: Optional[List[VorgangDeskriptor]] = None
    gesta: Optional[str] = Field(
        None,
        description='GESTA-Ordnungsnummer',
    )
    zustimmungsbeduerftigkeit: Optional[List[str]] = None
    kom: Optional[str] = Field(
        None,
        description='KOM-Nr.',
    )
    ratsdok: Optional[str] = Field(
        None,
        description='Ratsdok-Nr.',
    )
    verkuendung: Optional[List[Verkuendung]] = None
    inkrafttreten: Optional[List[Inkrafttreten]] = None
    archiv: Optional[str] = Field(
        None,
        description='Archivsignatur',
    )
    mitteilung: Optional[str] = Field(
        None,
    )
    vorgang_verlinkung: Optional[List[VorgangVerlinkung]] = None
    sek: Optional[str] = Field(
        None,
        description='SEK-Nr.',
    )


class Fundstelle(BaseModel):
    id: int = Field(
        ...,
        description='ID einer Drucksache oder eines Plenarprotokolls',
    )
    dokumentart: Dokumentart = Field(
        ...,
    )
    pdf_url: Optional[str] = Field(
        None,
    )
    dokumentnummer: str = Field(
        ...,
    )
    datum: date = Field(
        ...,
    )
    drucksachetyp: Optional[str] = Field(
        None,
    )
    herausgeber: Zuordnung = Field(
        ...,
    )
    urheber: List[str] = Field(
        ...,
    )
    verteildatum: Optional[date] = Field(
        None,
    )
    seite: Optional[str] = Field(
        None,
    )
    anfangsseite: Optional[int] = Field(
        None,
    )
    endseite: Optional[int] = Field(
        None,
    )
    anfangsquadrant: Optional[Quadrant] = Field(
        None,
    )
    endquadrant: Optional[Quadrant] = Field(
        None,
    )
    frage_nummer: Optional[str] = Field(
        None,
    )
    anlagen: Optional[str] = Field(
        None,
    )
    top: Optional[int] = Field(
        None,
    )
    top_zusatz: Optional[str] = Field(
        None,
    )


class PersonRole(BaseModel):
    funktion: str = Field(
        ...,
    )
    funktionszusatz: Optional[str] = Field(
        None,
    )
    fraktion: Optional[str] = Field(
        None,
    )
    nachname: str = Field(
        ...,
    )
    vorname: str = Field(
        ...,
    )
    namenszusatz: Optional[str] = Field(
        None,
    )
    wahlperiode_nummer: Optional[List[int]] = Field(
        None,
        description='Wahlperioden, für die der Personeneintrag zutrifft',
    )
    wahlkreiszusatz: Optional[str] = Field(
        None,
    )
    ressort_titel: Optional[str] = Field(
        None,
    )
    bundesland: Optional[Bundesland] = None


class VorgangListResponse(ListResponseBase):
    documents: List[Vorgang] = Field(...)


class Vorgangsposition(BaseModel):
    id: int = Field(
        ...,
    )
    vorgangsposition: str = Field(
        ...,
    )
    zuordnung: Zuordnung
    gang: bool = Field(
        ...,
        description='Alle Vorgangsschritte, die von besonderer Bedeutung für den Fortgang der Beratung sind, werden durch das Attribut `gang: true` gekennzeichnet.\n\nIst ein solcher Vorgangsschritt mit einer Drucksache verknüpft, werden im Frontend unter der Benennung "Wichtige Drucksachen" Herausgeber, Nummer und Typ sowie das Datum der entsprechenden Drucksachen ausgegeben (z.B. BT-Drs 18/13014 (Beschlussempfehlung), 28.06.2017). \nIst er mit einem Plenarprotokoll verknüpft, werden im Frontend unter der Benennung "Plenum" der Klartext der Vorgangsposition, Datum, Herausgeber und Nummer des Plenarprotokolls mit Anfangsseite/Quadrant und Endseite/Quadrant dargestellt (z.B. 2. Beratung: 29.06.2017, BT-PlPr 18/243, S. 24964C - 24973C).\n',
    )
    fortsetzung: bool = Field(
        ...,
        description='Erstreckt sich eine Beratung über mehrere Plenarprotokolle, so müssen entsprechend viele Vorgangsschritte mit je gleicher Vorgangsposition im Vorgangsablauf angelegt werden. Der zweite und jeder weitere dieser Schritte wird dann als "Fortsetzung" gekennzeichnet (Attribut `fortsetzung: true`). \nFür die Beratung des Gesetzentwurfs für die Feststellung des Haushaltsplanes (Haushaltsberatungen) gelten abweichende Regelungen.\n',
    )
    nachtrag: bool = Field(
        ...,
        description='Eine Auswertungseinheit eines Plenarprotokolls kann nur an genau einen Vorgangsschritt angebunden werden. \nMüssen aber mehrere Auswertungseinheiten für einen Vorgangsschritt gebildet werden (weil die Ergänzung einer Rede erst in einem späteren Protokoll erscheint oder weil sich z.B. bei einer Verbundenen Beratung (§ 24 GO-BT) nicht alle Schriftlichen Erklärungen nach § 31 GO-BT auf sämtliche Vorlagen beziehen), \ndann müssen im Vorgangsablauf mehrere Vorgangsschritte mit der gleichen Vorgangsposition angelegt werden. Der zweite und jeder weitere dieser Schritte wird dann als "Nachtrag" gekennzeichnet (Attribut `nachtrag: true`)\n',
    )
    vorgangstyp: str = Field(
        ...,
        description='Vorgangstyp des zugehörigen Vorgangs',
    )
    typ: VorgangspositionTyp = Field(
        ...,
    )
    titel: str = Field(
        ...,
        description='Titel des zugehörigen Vorgangs',
    )
    dokumentart: Dokumentart = Field(
        ...,
    )
    vorgang_id: int = Field(..., description='ID des zugehörigen Vorgangs')
    datum: date = Field(
        ...,
        description='Datum des zugehörigen Dokuments',
    )
    aktualisiert: datetime = Field(
        ...,
        description='Letzte Aktualisierung der Entität oder des zugehörigen Dokuments',
    )
    fundstelle: Fundstelle
    urheber: Optional[List[Urheber]] = None
    ueberweisung: Optional[List[Ueberweisung]] = None
    aktivitaet_anzeige: Optional[List[AktivitaetAnzeige]] = Field(
        None,
        description='Zusammenfassung der ersten 4 zur Anzeige vorgesehenen Aktivitäten',
    )
    aktivitaet_anzahl: int = Field(
        ...,
        description='Gesamtzahl der zugehörigen Aktivitäten',
    )
    ressort: Optional[List[Ressort]] = None
    beschlussfassung: Optional[List[Beschlussfassung]] = None
    ratsdok: Optional[str] = Field(
        None,
        description='Ratsdok-Nr.',
    )
    kom: Optional[str] = Field(
        None,
        description='KOM-Nr.',
    )
    sek: Optional[str] = Field(
        None,
        description='SEK-Nr.',
    )
    mitberaten: Optional[List[Vorgangspositionbezug]] = Field(
        None,
        description='Es ist eine häufig geübte Praxis, mehrere thematisch verwandte Vorlagen (z.B. konkurrierende Anträge der verschiedenen Fraktionen zum Thema Diesel-Fahrverbote) in einer Debatte gemeinsam zu beraten ("Zusammenberatung").\n\n`mitberaten` liefert, von einem Vorgang ausgehend, alle anderen Vorgänge, die Gegenstand der Zusammenberatung sind.\n',
    )
    abstract: Optional[str] = Field(
        None,
    )


class Drucksache(BaseModel):
    id: int = Field(
        ...,
    )
    typ: DokumentTyp = Field(
        ...,
    )
    dokumentart: DokumentartDrucksache = Field(
        ...,
    )
    drucksachetyp: str = Field(
        ...,
    )
    dokumentnummer: str = Field(
        ...,
    )
    wahlperiode: Optional[int] = Field(
        None,
    )
    herausgeber: Herausgeber = Field(
        ...,
    )
    datum: date = Field(
        ...,
    )
    aktualisiert: datetime = Field(
        ...,
        description='Letzte Aktualisierung der Entität',
    )
    titel: str = Field(
        ...,
    )
    autoren_anzeige: Optional[List[AutorenAnzeigeItem]] = Field(
        None,
        description='Zusammenfassung der ersten 4 zur Anzeige markierten Autor:innen',
    )
    autoren_anzahl: int = Field(
        ...,
        description='Gesamtzahl der Autor:innen',
    )
    fundstelle: Fundstelle
    pdf_hash: Optional[str] = Field(
        None,
        description='MD5-Prüfsumme der PDF-Datei',
    )
    urheber: Optional[List[Urheber]] = None
    vorgangsbezug: Optional[List[Vorgangsbezug]] = Field(
        None,
        description='Zusammenfassung der ersten 4 zugehörigen Vorgänge',
    )
    vorgangsbezug_anzahl: int = Field(
        ...,
        description='Gesamtzahl der zugehörigen Vorgänge',
    )
    ressort: Optional[List[Ressort]] = None
    anlagen: Optional[str] = Field(
        None,
    )


class Plenarprotokoll(BaseModel):
    id: int = Field(
        ...,
    )
    dokumentart: DokumentartPlenarprotokoll = Field(
        ...,
    )
    typ: DokumentTyp = Field(
        ...,
    )
    dokumentnummer: str = Field(
        ...,
    )
    wahlperiode: Optional[int] = Field(
        None,
    )
    herausgeber: Zuordnung
    datum: date = Field(
        ...,
    )
    aktualisiert: datetime = Field(
        ...,
        description='Letzte Aktualisierung der Entität',
    )
    titel: str = Field(
        ...,
    )
    fundstelle: Fundstelle
    pdf_hash: Optional[str] = Field(
        None,
        description='MD5-Prüfsumme der PDF-Datei',
    )
    vorgangsbezug: Optional[List[Vorgangsbezug]] = Field(
        None,
        description='Zusammenfassung der ersten 4 zugehörigen Vorgänge',
    )
    vorgangsbezug_anzahl: int = Field(
        ...,
        description='Gesamtzahl der zugehörigen Vorgänge',
    )
    sitzungsbemerkung: Optional[str] = Field(
        None,
    )


class DrucksacheText(Drucksache, DokumentTextBase):
    pass


class PlenarprotokollText(Plenarprotokoll, DokumentTextBase):
    pass


class Aktivitaet(BaseModel):
    id: int = Field(
        ...,
    )
    aktivitaetsart: str = Field(
        ...,
    )
    typ: AktivitaetTyp = Field(
        ...,
    )
    dokumentart: Dokumentart = Field(
        ...,
    )
    wahlperiode: int = Field(
        ...,
    )
    datum: date = Field(
        ...,
    )
    aktualisiert: datetime = Field(
        ...,
        description='Letzte Aktualisierung der Entität oder des zugehörigen Dokuments',
    )
    titel: str = Field(
        ...,
    )
    fundstelle: Fundstelle
    vorgangsbezug: Optional[List[Vorgangspositionbezug]] = Field(
        None,
        description='Zusammenfassung der ersten 4 zugehörigen Vorgänge',
    )
    vorgangsbezug_anzahl: int = Field(
        ...,
        description='Gesamtzahl der zugehörigen Vorgänge',
    )
    deskriptor: Optional[List[Deskriptor]] = None
    abstract: Optional[str] = Field(
        None,
    )


class Person(BaseModel):
    id: int = Field(
        ...,
    )
    nachname: str = Field(
        ...,
    )
    vorname: str = Field(
        ...,
    )
    namenszusatz: Optional[str] = Field(
        None,
    )
    typ: str = Field(
        ...,
    )
    wahlperiode: Optional[int] = Field(
        None,
        description='Wahlperiode des ersten zugehörigen Dokuments',
    )
    basisdatum: Optional[date] = Field(
        None,
        description='Datum des ersten zugehörigen Dokuments',
    )
    datum: Optional[date] = Field(
        None,
        description='Datum des letzten zugehörigen Dokuments',
    )
    aktualisiert: datetime = Field(
        ...,
        description='Letzte Aktualisierung der Entität',
    )
    titel: str = Field(
        ...,
    )
    person_roles: Optional[List[PersonRole]] = Field(
        None, description='Nebeneinträge mit bspw. abweichenden Funktionen oder Namensänderungen'
    )


class VorgangspositionListResponse(ListResponseBase):
    documents: List[Vorgangsposition] = Field(...)


class PlenarprotokollListResponse(ListResponseBase):
    documents: List[Plenarprotokoll] = Field(...)


class DrucksacheListResponse(ListResponseBase):
    documents: List[Drucksache] = Field(...)


class PlenarprotokollTextListResponse(ListResponseBase):
    documents: List[PlenarprotokollText] = Field(...)


class DrucksacheTextListResponse(ListResponseBase):
    documents: List[DrucksacheText] = Field(...)


class AktivitaetListResponse(ListResponseBase):
    documents: List[Aktivitaet] = Field(...)


class PersonListResponse(ListResponseBase):
    documents: List[Person] = Field(...)

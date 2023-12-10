from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_serializer

from backend.app.facades.deutscher_bundestag.model import Dokumentart, Zuordnung


class Format(str, Enum):
    """Format der Antwort."""

    JSON = "json"
    XML = "xml"


class CommonParameter(BaseModel):
    aktualisiert_start: Optional[datetime] = Field(
        default=None,
        description="Frühestes Aktualisierungsdatum der Entität",
        serialization_alias="f.aktualisiert.start",
    )

    aktualisiert_end: Optional[datetime] = Field(
        default=None,
        description="Spätestes Aktualisierungsdatum der Entität",
        serialization_alias="f.aktualisiert.end",
    )

    datum_start: Optional[date] = Field(
        default=None,
        description="Frühestes Datum der Entität",
        serialization_alias="f.datum.start",
    )

    datum_end: Optional[date] = Field(
        default=None,
        description="Spätestes Datum der Entität",
        serialization_alias="f.datum.end",
    )

    id: Optional[list[int]] = Field(
        default=None,
        description="ID der Entität (ODER-Suche)",
        serialization_alias="f.id",
    )

    vorgangstyp: Optional[list[str]] = Field(
        default=None,
        description="Vorgangstyp (ODER-Suche)",
        serialization_alias="f.vorgangstyp",
    )

    vorgangstyp_notation: Optional[list[int]] = Field(
        default=None,
        description="Vorgangstyp-Notation (ODER-Suche)",
        serialization_alias="f.vorgangstyp_notation",
    )

    wahlperiode: Optional[list[int]] = Field(
        default=None,
        description="Wahlperiode (ODER-Suche)",
        serialization_alias="f.wahlperiode",
    )

    cursor: Optional[str] = Field(
        default=None,
        description="Position des Cursors zur Anfrage weiterer Entitäten",
        serialization_alias="cursor",
    )

    format: Optional[Format] = Field(
        default=None,
        description="Steuert das Datenformat der Antwort, möglich sind JSON (voreingestellt) oder XML.",
        serialization_alias="format",
    )

    @field_serializer('aktualisiert_start', 'aktualisiert_end')
    def serialize_aktualisiert(self, value: datetime) -> str:
        """Serialize aktualisiert_start and aktualisiert_end in a format that is accepted by the API."""
        return value.strftime("%Y-%m-%dT%H:%M:%S")


class DokumentartParameter(BaseModel):
    dokumentart: Optional[Dokumentart] = Field(
        default=None,
        description="Selektiert alle Entitäten, die mit der angegebenen Dokumentart verknüpft sind.",
        serialization_alias="f.dokumentart",
    )

    dokumentnummer: Optional[list[str]] = Field(
        default=None,
        description="Dokumentnummer einer Drucksache oder eines Plenarprotokolls (ODER-Suche)",
        serialization_alias="f.dokumentnummer",
    )


class RessortfdfTitelUrheberParameter(BaseModel):
    ressort_fdf: Optional[list[str]] = Field(
        default=None,
        description="Ressort (federführend) (UND-Suche)",
        serialization_alias="f.ressort_fdf",
    )

    titel: Optional[list[str]] = Field(
        default=None,
        description="Titel (ODER-Suche. Eine Einzelwortsuche ist möglich. Mehrere Suchbegriffe hintereinander werden als Phrase gesucht.)",
        serialization_alias="f.titel",
    )

    urheber: Optional[list[str]] = Field(
        default=None,
        description="Urheber (UND-Suche)",
        serialization_alias="f.urheber",
    )


class RelatedDrucksacheParameter(BaseModel):
    drucksache: Optional[int] = Field(
        default=None,
        description="ID einer verknüpften Drucksache",
        serialization_alias="f.drucksache",
    )

    drucksachetyp: Optional[str] = Field(
        default=None,
        description="Typ der Drucksache",
        serialization_alias="f.drucksachetyp",
    )

    frage_nummer: Optional[list[str]] = Field(
        default=None,
        description="Fragenummer/Listenziffer (ODER-Suche)",
        serialization_alias="f.frage_nummer",
    )


class VorgangParameter(
    RelatedDrucksacheParameter,
    DokumentartParameter,
    RessortfdfTitelUrheberParameter,
    CommonParameter,
):
    beratungsstand: Optional[list[str]] = Field(
        default=None,
        description="Beratungsstand (ODER-Suche)",
        serialization_alias="f.beratungsstand",
    )

    deskriptor: Optional[list[str]] = Field(
        default=None,
        description="Deskriptor (UND-Suche)",
        serialization_alias="f.deskriptor",
    )

    gesta: Optional[list[str]] = Field(
        default=None,
        description="GESTA-Ordnungsnummer (ODER-Suche)",
        serialization_alias="f.gesta",
    )

    initiative: Optional[list[str]] = Field(
        default=None,
        description="Initiative (UND-Suche)",
        serialization_alias="f.initiative",
    )

    plenarprotokoll: Optional[int] = Field(
        default=None,
        description="ID eines verknüpften Plenarprotokolls",
        serialization_alias="f.plenarprotokoll",
    )

    sachgebiet: Optional[list[str]] = Field(
        default=None,
        description="Sachgebiet (UND-Suche)",
        serialization_alias="f.sachgebiet",
    )

    verkuendung_fundstellen: Optional[list[str]] = Field(
        default=None,
        description="Fundstelle der Verkündung (ODER-Suche. Einzelwortsuche (z.B. nach dem Verkündungsblatt) ist möglich)",
        serialization_alias="f.verkuendung_fundstellen",
    )


class VorgangspositionParameter(
    RelatedDrucksacheParameter,
    DokumentartParameter,
    RessortfdfTitelUrheberParameter,
    CommonParameter,
):
    aktivitaet: Optional[int] = Field(
        default=None,
        description="ID einer verknüpften Aktivität",
        serialization_alias="f.aktivitaet",
    )

    plenarprotokoll: Optional[int] = Field(
        default=None,
        description="ID eines verknüpften Plenarprotokolls",
        serialization_alias="f.plenarprotokoll",
    )

    vorgang: Optional[int] = Field(
        default=None,
        description="ID eines verknüpften Vorgangs",
        serialization_alias="f.vorgang",
    )
    zuordnung: Optional[Zuordnung] = Field(
        default=None,
        description="Zuordnung der Entität zum Bundestag, Bundesrat, Bundesversammlung oder Europakammer (UND-Suche)",
        serialization_alias="f.zuordnung",
    )


class DrucksacheParameter(CommonParameter, RessortfdfTitelUrheberParameter):
    dokumentnummer: Optional[list[str]] = Field(
        default=None,
        description="Dokumentnummer einer Drucksache oder eines Plenarprotokolls (ODER-Suche)",
        serialization_alias="f.dokumentnummer",
    )

    drucksachetyp: Optional[str] = Field(
        default=None,
        description="Typ der Drucksache",
        serialization_alias="f.drucksachetyp",
    )

    zuordnung: Optional[Zuordnung] = Field(
        default=None,
        description="Zuordnung der Entität zum Bundestag, Bundesrat, Bundesversammlung oder Europakammer (UND-Suche)",
        serialization_alias="f.zuordnung",
    )


class PlenarprotokollParameter(CommonParameter):
    dokumentnummer: Optional[list[str]] = Field(
        default=None,
        description="Dokumentnummer einer Drucksache oder eines Plenarprotokolls (ODER-Suche)",
        serialization_alias="f.dokumentnummer",
    )

    zuordnung: Optional[Zuordnung] = Field(
        default=None,
        description="Zuordnung der Entität zum Bundestag, Bundesrat, Bundesversammlung oder Europakammer (UND-Suche)",
        serialization_alias="f.zuordnung",
    )

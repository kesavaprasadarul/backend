"""Contains ressorts."""

from enum import StrEnum


class BUNDESTAG_RESSORT(StrEnum):
    """Contains ressorts."""

    WIRTSCHAFT = "Wirtschaft"
    FINANZEN = "Finanzen"
    INNENPOLITIK = "Innenpolitik"
    AUSSENPOLITIK = "Außenpolitik"
    JUSTIZ = "Justiz"
    ARBEIT = "Arbeit"
    VERTEIDIGUNG = "Verteidigung"
    LANDWIRTSCHAFT = "Landwirtschaft"
    FAMILIE = "Familie"
    GESUNDHEIT = "Gesundheit"
    VERKEHR_UND_DIGITALISIERUNG = "Verkehr und Digitalisierung"
    UMWELT = "Umwelt"
    BILDUNG_UND_FORSCHUNG = "Bildung und Forschung"
    ENTWICKLUNG = "Entwicklung"
    WOHNUNGSBAU = "Wohnungsbau"


"""Contains subset of ressorts that are used for bundestag top topics."""
RESSORT_SUBSTITUTIONS = {
    BUNDESTAG_RESSORT.WIRTSCHAFT: ["Wirtschaft", 'Klimaschutz'],
    BUNDESTAG_RESSORT.FINANZEN: ["Finanzen"],
    BUNDESTAG_RESSORT.INNENPOLITIK: ["Innenpolitik", 'Heimat'],
    BUNDESTAG_RESSORT.AUSSENPOLITIK: ["Außenpolitik"],
    BUNDESTAG_RESSORT.JUSTIZ: ["Justiz"],
    BUNDESTAG_RESSORT.ARBEIT: ["Arbeit", 'Soziales'],
    BUNDESTAG_RESSORT.VERTEIDIGUNG: ["Militär"],
    BUNDESTAG_RESSORT.LANDWIRTSCHAFT: ["Ernährung", "Landwirtschaft"],
    BUNDESTAG_RESSORT.FAMILIE: ["Familie"],  # , "Senioren"]
    BUNDESTAG_RESSORT.GESUNDHEIT: ["Gesundheit"],
    BUNDESTAG_RESSORT.VERKEHR_UND_DIGITALISIERUNG: ["Digitales", "Verkehr"],
    BUNDESTAG_RESSORT.UMWELT: ["Umwelt", 'Naturschutz', 'nukleare Sicherheit', 'Verbraucherschutz'],
    BUNDESTAG_RESSORT.BILDUNG_UND_FORSCHUNG: ["Bildung", "Forschung"],
    BUNDESTAG_RESSORT.ENTWICKLUNG: ["Entwicklung", 'wirtschaftliche Zusammenarbeit'],
    BUNDESTAG_RESSORT.WOHNUNGSBAU: ["Wohnungsbau", 'Wohnen', 'Stadtentwicklung', 'Bauwesen'],
}

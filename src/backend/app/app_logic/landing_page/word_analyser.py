import fasttext
import fasttext.util  # use pip install fasttext-wheel
import os
import shutil
import re
from backend.app.utils import get_data_folder
from backend.app.core.logging import configure_logging

# import nltk
import numpy as np

# from nltk.corpus import stopwords
from logging import getLogger

logger = getLogger(__name__)


# A class that represents a file and allows querying and analysing its content
class WordCounter:
    ressortsText = [
        "Wirtschaft",
        "Finanzen",
        "Innenpolitik",
        "Außenpolitik",
        "Justiz",
        "Arbeit",
        "Verteidingung",
        "Landwirtschaft",
        "Familie",
        "Gesundheit",
        "Digitalisierung",
        "Verkehr",
        "Umwelt",
        "Bildung",
        "Forschung",
        "Wohnungsbau",
    ]

    def __init__(self, wordlist):
        self.wordlist = wordlist

        model_path = "models/cc.de.300.bin"
        model_path = os.path.join(get_data_folder(), model_path)

        # Download the fasttext model for German if it is not already downloaded
        if not os.path.isfile(model_path):
            logger.info("Downloading fasttext model")
            file_name = fasttext.util.download_model('de', if_exists='ignore')  # English

            logger.info("Moving fasttext model to %s", model_path)

            shutil.move(file_name, model_path)

            if os.path.isfile(file_name + ".gz"):
                os.remove(file_name + ".gz")
        logger.info("Loading fasttext model from %s", model_path)
        self.ft = fasttext.load_model(model_path)  # German vocabulary , trained on Wikipedia

    # Maps a word to a vector, currently just by a library call
    def __wtv(self, word):
        return self.ft.get_word_vector(word)

    def word_count(self):
        counts = dict()
        for word in self.wordlist:
            if word in counts:
                counts[word] += 1
            else:
                counts[word] = 1
        return counts
        # return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))

    # Returns a dictionary that maps a word to the resort that is most similar to it accord to the word embedding
    def word_to_ressort(self):
        dict_w_res = dict()
        for word_t in set(self.wordlist):
            percent = 0
            for res in self.ressortsText:
                divisor = np.linalg.norm(self.__wtv(word_t)) * np.linalg.norm(self.__wtv(res))
                if divisor > 0:
                    val = np.dot(self.__wtv(word_t), self.__wtv(res)) / divisor
                    if percent < val:
                        percent = val
                        dict_w_res[word_t] = res
        return dict_w_res

    def remove_words(self):
           german_articles = {
            # Nominative
            'Der',
            'Die',
            'Das',
            'Ein',
            'Eine',
            # Accusative
            'Den',
            'Die',
            'Das',
            'Einen',
            'Eine',
            'Ein',
            # Dative
            'Dem',
            'Der',
            'Dem',
            'Einem',
            'Einer',
            'Einem',
            # Genitive
            'Des',
            'Der',
            'Des',
            'Eines',
            'Einer',
            'Eines',
            # Plural forms
            'Die',
            'Die',
            'Die',
            'Keine',
            # Special forms
            'Zur',
            'Zum',
            'Zur',
            'Zur',
            'Zu den',
            'Zu der',
            'Zu dem',
            'Zu der',
            'Dessen',
            'Deren',
            # Common prepositions
            'Mit',
            'Ohne',
            'An',
            'Auf',
            'In',
            'Unter',
            'Über',
            'Vor',
            'Hinter',
            'Neben',
            'Zwischen',
            'Bei',
            'Nach',
            'Seit',
            'Während',
            'Gegenüber',
            # Interrogative pronouns
            'Wer',
            'Was',
            'Wessen',
            'Wem',
            'Wen',
            # Demonstrative pronouns
            'Dieser',
            'Diese',
            'Dieses',
            'Diese',
            'Dieses',
            'Dieser',
            'Diesen',
            'Dieser',
            'Diesem',
            'Diesem',
            # Relative pronouns
            'Der',
            'Die',
            'Das',
            'Denen',
            # Conjunctions
            'Und',
            'Oder',
            'Aber',
            'Denn',
            # Präpositionen (Prepositions)
            'Mit',
            'Ohne',
            'An',
            'Auf',
            'In',
            'Unter',
            'Über',
            'Vor',
            'Hinter',
            'Neben',
            'Zwischen',
            'Bei',
            'Nach',
            'Seit',
            'Während',
            'Gegenüber',
            'Außerhalb',
            'Innerhalb',
            'Entlang',
            'Durch',
            'Für',
            'Wegen',
            'Trotz',
            'Bis',
            'Zu',
            # Personal pronouns
            'Ich',
            'Du',
            'Er',
            'Sie',
            'Es',
            'Wir',
            'Ihr',
            'Sie',
            'Sie',
            # Reflexive pronouns
            'Mich',
            'Dich',
            'Sich',
            'Uns',
            'Euch',
            'Sich',
            'Sich',
            # Possessive pronouns
            'Mein',
            'Dein',
            'Sein',
            'Ihr',
            'Sein',
            'Unser',
            'Euer',
            'Ihr',
            'Ihr',
            'Meiner',
            'Deiner',
            'Seiner',
            'Ihrer',
            'Seiner',
            'Unser',
            'Euer',
            'Ihrer',
            'Ihrer',
            'Meins',
            'Deins',
            'Seins',
            'Ihres',
            'Seins',
            'Unser',
            'Euer',
            'Ihres',
            'Ihres',
            'Meinem',
            'Deinem',
            'Seinem',
            'Ihrem',
            'Seinem',
            'Unserem',
            'Eurem',
            'Ihrem',
            'Ihrem',
            'Meinen',
            'Deinen',
            'Seinen',
            'Ihren',
            'Seinen',
            'Unseren',
            'Euren',
            'Ihren',
            'Ihren',
            # Demonstrative pronouns
            'Dieser',
            'Diese',
            'Dieses',
            'Jener',
            'Jene',
            'Jenes',
            # Relative pronouns
            'Der',
            'Die',
            'Das',
            'Denen',
            'Welcher',
            'Welche',
            'Welches',
            # Interrogative pronouns
            'Wer',
            'Wen',
            'Wem',
            'Wessen',
            'Was',
            'Welcher',
            'Welche',
            'Welches',
            # Indefinite pronounss
            'Alle',
            'Viele',
            'Einige',
            'Jeder',
            'Jede',
            'Jedes',
            'Manche',
            'Irgendein',
            'Irgendeine',
            'Irgendein',
        }
        #TOP 100 words thaat  appear at leaast 20 times (extracted over all protocols of 2023)

        top100= ['13', 'Bundesregierung', 'Entlastung', 'Ausschuss', 'Antwort', 'Olaf', 'Annahme', 'Ordnungsrufes',
                 'EUZBBG',
                 'Deutschlands', 'Entscheidung', '6.', 'Beschleunigung', 'Bundes', '50', 'Fraktion', 'EP',
                 'Gesetzentwurf',
                 'Einfügung', 'Erteilung', 'Finanzierung', '10', 'Klimaschutz', 'Prüfung', 'BÜNDNIS', 'Verwendung',
                 'Erneute',
                 'Angabe', 'Ausschusses:', 'Parlament', 'Unternehmen', 'Deutschland', 'November', 'Deutsche',
                 'Europäische',
                 'Juli', 'Parlament,', 'Sicherstellung', 'Anlage', 'Robert', 'Titeländerung', 'Bundesministerium',
                 'Verordnungsermächtigung<br', 'Bereich', 'Einrichtung', 'Auffassung', 'Vorschriften', 'Wann', 'Rat',
                 'Übertragung', 'Anwendung', 'BvR', 'Indikativen', 'Fortsetzung', 'Ausschusses:</strong>', 'Oktober',
                 'Vorhaben', 'Feststellung', 'Standards', 'Verbesserung', 'Hat', 'Regelung', 'Sozialausschuss',
                 'Bundestagsdrucksache', 'Mitglieder', 'Abg', 'Siehe', 'Beendigung', 'Ländern', 'Russland',
                 'Petitionsausschusses', 'Bundesministeriums', 'Empfehlung', 'Verzicht', 'Fragestunde',
                 'Berücksichtigung',
                 '25.', '6', 'Januar', 'Möglichkeit', 'Anerkennung', '9', 'SPD,', 'L', 'Aufnahme', 'Unterrichtung',
                 'Einführung', 'Klarstellungen', 'Ausgaben', 'Entwicklung', 'Bundesminister', 'Anlagen', 'Zusammenhang',
                 '12',
                 'Ausweitung', 'Bund', 'FDP', 'Lage', '20.', '11', 'Sammelübersicht', 'Neufassung', 'Jahre',
                 'Weiterentwicklung', 'Personen', 'Verordnung', 'Deutschen', 'EuB-BReg', '2016', 'Bekämpfung',
                 'September',
                 '(bitte', '26.', 'Zugang', '(2.', '17.', 'Bildung', 'Entschließung', 'Beibehaltung', 'Union',
                 'Kommission',
                 'Zustimmung', 'Bundestages', 'Ergänzung', 'Ausschuss)', 'Förderung', 'Bewertung', '1.', 'Durchführung',
                 '2',
                 '2022', 'Hintergrund', '21.', '(EG)', 'Dezember', '30', 'WP', 'Buch', 'KOM(2022)', 'Jahr', 'Vorlage,',
                 'Petitionen', 'Absenkung', '20', '1)<br', 'Daten', 'Gesetz', 'Aussprache', 'Kenntnis', '(Anlage', '7',
                 'Forschung', '8', 'Frage(n):<br', 'Richtlinien', 'Nr.', 'Grundlage', 'Dr.', 'Arbeit', 'Verfahren',
                 'Versorgung', 'Begrüßung', 'Klarstellung', 'Schutz', 'Ausbau', '1', '(GASP/GSVP)', 'Unterstützung',
                 'April',
                 'Nutzung', 'Parlaments', 'Sondervermögens', 'Stand', 'Hinblick', 'Reduzierung', 'Rat,',
                 'Folgeänderungen',
                 '31.', 'Vorlage', 'Sicht', '13.', '19.', 'Internationalen', 'Rahmen', '2020', 'Zusätzliche',
                 'Festlegung',
                 '&ndash;', 'Höhe', 'Euro,', 'Bundesrepublik', '14', 'Richtlinie', 'Status', 'Absatz', '(EU)',
                 'Übereinkommens',
                 'Mitteln', 'Verlängerung', 'Digitales', 'Digitalisierung', 'Koalitionsvertrag', 'Ermöglichung',
                 'Schaffung',
                 '2024', 'Europa', 'Vorschau', '2025', 'Anforderungen', 'Informationen', 'Aufhebung', 'Namen',
                 'Zusammenarbeit',
                 'Europäischen', 'Abgabe', 'Rechtsverordnungen;', 'GESTA', 'Wirtschafts-', 'Staaten', '(ABl.', 'Wahl',
                 'Reform',
                 'Soldaten,', 'Menschen', 'Mrd', 'Erweiterung', 'Republik', 'Art.', 'Verkehr', 'Regelungen',
                 'Sanktionen:',
                 'Verhinderung', 'Prozent', '<br', 'Sicherung', 'EU', '90/DIE', 'Auswirkungen', 'Vorgaben', 'GRÜNEN',
                 'Rates',
                 'Bezug', '24.', 'März', 'Energien', 'Investitionen', 'Verpflichtung', 'Kosten', '(eingebracht', '2.',
                 'Wärmeplanung', 'Bezug:', 'Evaluierung', 'Erleichterung', '3', 'Anzahl', 'Bericht', 'Mitteilung',
                 'Anhebung',
                 'Regionen', 'Einhaltung', 'Sozial', 'Verbot', 'Änderungen', 'Euro', '2023', 'Bundeshaushalt',
                 'Mitgliedstaaten', 'Bereitstellung', 'S.', 'Anpassungen', 'Recht', ';', '29.', '2024,', 'Rechts',
                 '2019',
                 'Gebäudeenergie', 'Gewährleistung', 'Verteidigung', 'Mio', 'Mai', 'Aufbau', 'Bundesministerin',
                 'Bundeswehr',
                 'Juni', 'Steigerung', '2021', 'Vermeidung', 'Einsatz', 'Modernisierung', 'Februar', 'Vorschlag',
                 'Beschlusses',
                 'Pflicht', 'Gesetzen', 'Soldaten', '§', 'Änderung', 'Beteiligung', 'Anpassung', 'BT-Drs', 'Umsetzung',
                 'Entschließungsantrag', 'Bundesministers', 'Ende', '<strong>Beschlussempfehlung', 'Wirtschaft', '23',
                 'KOM(2023)', 'Mittel', 'Originaltext', 'Stärkung', 'Wie', 'Stellungnahme', 'Anträge',
                 'Verordnungsermächtigung', '(AfD)', '(vgl.', 'Kommunen', '7.', 'Gesetzes', 'Länder', 'Beschluss', '-',
                 'Verlangen', 'Ratsdok.', 'Frage', 'Streitkräfte', '15', '2022)', 'AG', 'Jahren', 'Erhöhung',
                 'Bundestag',
                 '15.', 'Bundesregierung,', '2023,', 'Maßnahmen', 'Sicherheit', 'Übereinkommen', '30.', 'Gemeinsamer',
                 '2018',
                 'Vereinbarung']
        self.wordlist=[word for word in self.wordlist if word not in top100]

        #remove nonalphabetical chars
        regex = re.compile('[^a-zA-ZÄÖÜäöüß]')
        # Use list comprehension to apply the regex and filter the list
        self.wordlist = [regex.sub('', item) for item in self.wordlist]

        self.wordlist = [
            word for word in self.wordlist
            if not (word[0].islower() or word in german_articles)
        ]

    def make_word_cloud(self):
        self.remove_words()
        dictionary_counts = self.word_count()
        ressort_to_words = {}
        for word, ressort in self.word_to_ressort().items():
            if ressort in ressort_to_words:
                ressort_to_words[ressort].append((word, dictionary_counts.get(word)))
            else:
                ressort_to_words[ressort] = [(word, dictionary_counts.get(word))]
        return ressort_to_words


def main():
    wordlist = [
        "Überschwemmung",
        "Flut",
        "Kindergarten",
        "Syrien",
        "das",
        "Der",
        "Krieg",
        "Ukraine",
        "EZB",
        "Digitalisierungsgesetz",
        "Syrien",
        "Krieg",
        "Krieg",
    ]
    instance = WordCounter(wordlist)
    print("start")
    print(instance.make_word_cloud())


if __name__ == "__main__":
    configure_logging()
    main()

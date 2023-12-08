import os
import re
import shutil

# from nltk.corpus import stopwords
from logging import getLogger

import fasttext
import fasttext.util  # use pip install fasttext-wheel

# import nltk
import numpy as np

from backend.app.core.bundestag_ressorts import BUNDESTAG_RESSORTS
from backend.app.core.logging import configure_logging
from backend.app.utils import get_data_folder

logger = getLogger(__name__)


# A class that represents a file and allows querying and analysing its content
class WordCounter:
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
            for res in BUNDESTAG_RESSORTS:
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
        # TOP 100 words thaat  appear at leaast 20 times (extracted over all protocols of 2023)

        top100 = [
            '13',
            'Bundesregierung',
            'Entlastung',
            'Ausschuss',
            'Antwort',
            'Olaf',
            'Annahme',
            'Ordnungsrufes',
            'EUZBBG',
            'Deutschlands',
            'Entscheidung',
            '6.',
            'Beschleunigung',
            'Bundes',
            '50',
            'Fraktion',
            'EP',
            'Gesetzentwurf',
            'Einfügung',
            'Erteilung',
            'Finanzierung',
            '10',
            'Prüfung',
            'BÜNDNIS',
            'Verwendung',
            'Erneute',
            'Angabe',
            'Ausschusses:',
            'Parlament',
            'Unternehmen',
            'Deutschland',
            'November',
            'Deutsche',
            'Europäische',
            'Juli',
            'Parlament,',
            'Sicherstellung',
            'Anlage',
            'Robert',
            'Titeländerung',
            'Bundesministerium',
            'Verordnungsermächtigung<br',
            'Bereich',
            'Einrichtung',
            'Auffassung',
            'Vorschriften',
            'Wann',
            'Rat',
            'Übertragung',
            'Anwendung',
            'BvR',
            'Indikativen',
            'Fortsetzung',
            'Ausschusses:</strong>',
            'Oktober',
            'Vorhaben',
            'Feststellung',
            'Standards',
            'Verbesserung',
            'Hat',
            'Regelung',
            'Sozialausschuss',
            'Bundestagsdrucksache',
            'Mitglieder',
            'Abg',
            'Siehe',
            'Beendigung',
            'Ländern',
            'Petitionsausschusses',
            'Bundesministeriums',
            'Empfehlung',
            'Verzicht',
            'Fragestunde',
            'Berücksichtigung',
            '25.',
            '6',
            'Januar',
            'Möglichkeit',
            'Anerkennung',
            '9',
            'SPD,',
            'L',
            'Aufnahme',
            'Unterrichtung',
            'Einführung',
            'Klarstellungen',
            'Ausgaben',
            'Entwicklung',
            'Bundesminister',
            'Anlagen',
            'Zusammenhang',
            '12',
            'Ausweitung',
            'Bund',
            'FDP',
            'Lage',
            '20.',
            '11',
            'Sammelübersicht',
            'Neufassung',
            'Jahre',
            'Weiterentwicklung',
            'Personen',
            'Verordnung',
            'Deutschen',
            'EuB-BReg',
            '2016',
            'Bekämpfung',
            'September',
            '(bitte',
            '26.',
            'Zugang',
            '(2.',
            '17.',
            'Entschließung',
            'Beibehaltung',
            'Union',
            'Kommission',
            'Zustimmung',
            'Bundestages',
            'Ergänzung',
            'Ausschuss)',
            'Förderung',
            'Bewertung',
            '1.',
            'Durchführung',
            '2',
            '2022',
            'Hintergrund',
            '21.',
            '(EG)',
            'Dezember',
            '30',
            'WP',
            'Buch',
            'KOM(2022)',
            'Jahr',
            'Vorlage,',
            'Petitionen',
            'Absenkung',
            '20',
            '1)<br',
            'Daten',
            'Gesetz',
            'Aussprache',
            'Kenntnis',
            '(Anlage',
            '7',
            'Forschung',
            '8',
            'Frage(n):<br',
            'Richtlinien',
            'Nr.',
            'Grundlage',
            'Dr.',
            'Arbeit',
            'Verfahren',
            'Versorgung',
            'Begrüßung',
            'Klarstellung',
            'Schutz',
            'Ausbau',
            '1',
            '(GASP/GSVP)',
            'Unterstützung',
            'April',
            'Nutzung',
            'Parlaments',
            'Sondervermögens',
            'Stand',
            'Hinblick',
            'Reduzierung',
            'Rat,',
            'Folgeänderungen',
            '31.',
            'Vorlage',
            'Sicht',
            '13.',
            '19.',
            'Internationalen',
            'Rahmen',
            '2020',
            'Zusätzliche',
            'Festlegung',
            '&ndash;',
            'Höhe',
            'Euro,',
            'Bundesrepublik',
            '14',
            'Richtlinie',
            'Status',
            'Absatz',
            '(EU)',
            'Übereinkommens',
            'Mitteln',
            'Verlängerung',
            'Koalitionsvertrag',
            'Ermöglichung',
            'Schaffung',
            '2024',
            'Europa',
            'Vorschau',
            '2025',
            'Anforderungen',
            'Informationen',
            'Aufhebung',
            'Namen',
            'Zusammenarbeit',
            'Europäischen',
            'Abgabe',
            'Rechtsverordnungen;',
            'GESTA',
            'Wirtschafts-',
            'Staaten',
            '(ABl.',
            'Wahl',
            'Reform',
            'Menschen',
            'Mrd',
            'Erweiterung',
            'Republik',
            'Art.',
            'Regelungen',
            'Verhinderung',
            'Prozent',
            '<br',
            'Sicherung',
            'EU',
            '90/DIE',
            'Auswirkungen',
            'Vorgaben',
            'GRÜNEN',
            'Rates',
            'Bezug',
            '24.',
            'März',
            'Investitionen',
            'Verpflichtung',
            'Kosten',
            '(eingebracht',
            '2.',
            'Bezug:',
            'Evaluierung',
            'Erleichterung',
            '3',
            'Anzahl',
            'Bericht',
            'Mitteilung',
            'Anhebung',
            'Regionen',
            'Einhaltung',
            'Sozial',
            'Verbot',
            'Änderungen',
            'Euro',
            '2023',
            'Bundeshaushalt',
            'Mitgliedstaaten',
            'Bereitstellung',
            'S.',
            'Anpassungen',
            'Recht',
            ';',
            '29.',
            '2024,',
            'Rechts',
            '2019',
            'Gewährleistung',
            'Verteidigung',
            'Mio',
            'Mai',
            'Aufbau',
            'Bundesministerin',
            'Juni',
            'Steigerung',
            '2021',
            'Vermeidung',
            'Einsatz',
            'Modernisierung',
            'Februar',
            'Vorschlag',
            'Beschlusses',
            'Pflicht',
            'Gesetzen',
            'Soldaten',
            '§',
            'Änderung',
            'Beteiligung',
            'Anpassung',
            'BT-Drs',
            'Umsetzung',
            'Entschließungsantrag',
            'Bundesministers',
            'Ende',
            '<strong>Beschlussempfehlung',
            'Wirtschaft',
            '23',
            'KOM(2023)',
            'Mittel',
            'Originaltext',
            'Stärkung',
            'Wie',
            'Stellungnahme',
            'Anträge',
            'Verordnungsermächtigung',
            '(AfD)',
            '(vgl.',
            'Kommunen',
            '7.',
            'Gesetzes',
            'Länder',
            'Beschluss',
            '-',
            'Verlangen',
            'Ratsdok.',
            'Frage',
            '15',
            '2022)',
            'AG',
            'Jahren',
            'Erhöhung',
            'Bundestag',
            '15.',
            'Bundesregierung,',
            '2023,',
            'Maßnahmen',
            'Sicherheit',
            'Übereinkommen',
            '30.',
            'Gemeinsamer',
            '2018',
            'Vereinbarung', "Debatte", "Mögliche", "Schlussfolgerungen", "Verordnungen", "Erlass", "Instrument",
            "Veröffentlichung", "Thema", "Entscheidungen", "Bewältigung", "Allgemeine", "Zahlen", "Vertrag", "Position",
            "Fonds", "Fünftes", "Bereichen","Staates","GmbH","Rechte","Erklärung","Erhalt", "Staat", "Historische"
        ]
        abgeordnete = ['Nancy', 'Thies', 'Klein-Schmeink', 'Diaby', 'Jan', 'Schenderlein', 'Bengt', 'Bareiß', 'Marlon',
                       'Gnauck', 'Reinhold', 'Isabel', 'Chantal', 'Uhlig', 'Sascha', 'Kassem', 'Schahina', 'Menge',
                       'Rosenthal', 'Kippels', 'Sattelberger', 'Höferlin', 'Ye-One', 'Dunja', 'Gröhe', 'Kersten',
                       'Wagner', 'Karamba', 'Domscheit-Berg', 'Harzer', 'Schraps', 'Bärbel', 'Karsten', 'Thews',
                       'Limbacher', 'Denise', 'Sven', 'Karoline', 'Schauws', 'Wegge', 'Bergt', 'Artur', 'Klöckner',
                       'Boris', 'Wundrak', 'Lennard', 'Graf', 'Joana', 'Gülistan', 'Frömming', 'Durz', 'Cademartori',
                       'Macit', 'Lemke', 'Dietrich', 'Rüffer', 'Vries', 'Zeulner', 'Echeverria', 'Hanke', 'Rößner',
                       'Polat', 'Pantazis', 'Reinalter', 'Espendiller', 'Schiefner', 'Tobias', 'Sthamer', 'Mehmet',
                       'Karlheinz', 'Bochmann', 'Weiss', 'Chrupalla', 'Rainer', 'Ingmar', 'Vogt', 'Kindler', 'Redder',
                       'Stein', 'Hirte', 'Habeck', 'Weidel', 'Anja', 'Renner', 'Erndl', 'Ridder', 'B.', 'Geissler',
                       'Hans-Jürgen', 'Ziegler', 'Karl', 'Grützmacher', 'Helferich', 'Maas', 'Kubicki', 'Akbulut',
                       'Röttgen', 'Oppelt', 'Breilmann', 'Malte', 'Lange', 'Scheer', 'Ingeborg', 'Meyer', 'Rolf',
                       'Dennis', 'Hostert', 'Andrew', 'Marcus', 'Ramsauer', 'Falko', 'Marja-Liisa', 'Dürr',
                       'Schulz-Asche', 'Riexinger', 'Lutze', 'Alabali-Radovan', 'Hennig-Wellsow', 'Kleinwächter',
                       'Abdi', 'Breher', 'Leikert', 'Beate', 'Friedrich', 'BeekBarbara', 'Achim', 'Nastić', 'Protschka',
                       'Stefinger', 'Papenbrock', 'Lindh', 'Tino', 'Judith', 'Ralph', 'Dietmar', 'Dilcher', 'Annika',
                       'Torsten', 'Josip', 'Lührmann', 'Serap', 'Müntefering', 'Wallstein', 'Hubert', 'Dagmar',
                       'Lindemann', 'Bernd', 'Griese', 'Mahmut', 'Maria-Lena', 'Bühl', 'Götz', 'Brand', 'Kühnert',
                       'Lucks', 'Maria', 'Faber', 'Trittin', 'Gramling', 'Wiehle', 'Jessica', 'Philip', 'Droßmann',
                       'Sandra', 'Parsa', 'Eugen', 'Auernhammer', 'Roderich', 'Mordhorst', 'Koob', 'Moll', 'Brodesser',
                       'Paus', 'Christina-Johanne', 'Tillmann', 'Hunko', 'Heiko', 'Björn', 'Gottschalk', 'Baumann',
                       'Esken', 'Khan', 'Schäuble', 'Willsch', 'Eichwede', 'Rhie', 'König', 'Rita', 'Laura', 'Stetten',
                       'Vogler', 'Merle', 'Canan', 'Mast', 'Reichinnek', 'Ryglewski', 'FirnhaberChristian', 'Nyke',
                       'Martens', 'Gesine', 'Kaweh', 'Hardt', 'Verlinden', 'Nezahat', 'Andrea', 'Heveling', 'Kreiser',
                       'Lisa', 'Mansmann', 'Kleebank', 'Helge', 'Damerow', 'Launert', 'Zanda', 'Friedhelm', 'Zoe',
                       'Miersch', 'Anne-Monika', 'Erwin', 'Thomae', 'Anna', 'Brinkhaus', 'Vontz', 'Klingbeil', 'Mohrs',
                       'Lehmann', 'Scheuer', 'Nadine', 'Todtenhausen', 'Oehl', 'Stöber', 'Wegling', 'Zorn', 'Fabian',
                       'Max', 'Ingo', 'Steffi', 'Taher', 'Fritz', 'Peter', 'Nick', 'Steiniger', 'Laschet', 'Naujok',
                       'Raffelhüschen', 'Loos', 'Esra', 'Stier', 'Roger', 'Valentin', 'Grosse-Brömer', 'Petra', 'Felix',
                       'Deborah', 'Schmidt', 'Jana', 'Stockmeier', 'Henneberger', 'Kühn', 'Brandl', 'Melanie', 'Felser',
                       'Fester', 'Hannes', 'Rohwer', 'Markus', 'Gerold', 'Schmid', 'Jarzombek', 'Franke', 'Nürnberger',
                       'Natalie', 'Gerald', 'Bas', 'Bröhr', 'Bayram', 'Boehringer', 'Feiler', 'Gava', 'Lay', 'Ruppert',
                       'Walter', 'Jörn', 'Bartsch', 'Heselhaus', 'Julian', 'Lenkert', 'Brandner', 'Jamila', 'Reem',
                       'Beatrix', 'Koeppen', 'Westig', 'Sebastian', 'Walter-Rosenheimer', 'Janine', 'Wittmann', 'Oßner',
                       'Nicolas', 'Connemann', 'Außendorf', 'Simone', 'Schulz', 'Nils', 'Bruno', 'Irlstorfer', 'Irene',
                       'Christina', 'Müller', 'Röwekamp', 'Schwartze', 'Holger', 'Busen', 'Poschmann', 'Niklas', 'Loop',
                       'Moritz', 'Leye', 'von', 'Stadler', 'Mareike', 'Anette', 'Sevim', 'Funke-Kaiser', 'Christian',
                       'Konstantin', 'Nolte', 'Wiener', 'Hermann', 'Tanja', 'Hacker', 'Benner', 'Gabriela', 'Siemtje',
                       'Schimke', 'Martin', 'Daniel', 'Adis', 'André', 'Axel', 'Robin', 'Coße', 'Nanni', 'Kirsten',
                       'Elisabeth', 'Heidi', 'Leiser', 'Andres', 'Schreider', 'Mack', 'Kevin', 'Mörseburg', 'Seidler',
                       'Whittaker', 'Dahmen', 'Weishaupt', 'Simona', 'Link', 'Scholz', 'Hümpfer', 'Arlt', 'Gebhart',
                       'Gregor', 'Alois', 'Rudolph', 'Rouenhoff', 'Susanne', 'Rohde', 'Hoppenstedt',
                       'Timmermann-Fechter', 'Mehltretter', 'Schulze', 'Hermann-Josef', 'Ingrid', 'Kappert-Gonther',
                       'Keller', 'Görke', 'Throm', 'Gutting', 'Norbert', 'Rottmann', 'Dorothee', 'Helling-Plahr',
                       'Hofreiter', 'Wadephul', 'Sylvia', 'Alt', 'Carlos', 'Bubendorfer-Licht', 'Yvonne', 'Ahmetovic',
                       'Semet', 'Hessel', 'dos', 'Rinck', 'Ulle', 'Georg', 'Kluckert', 'Kaczmarek', 'Janosch', 'Otten',
                       'Fricke', 'Sitte', 'Saskia', 'Ann-Veruschka', 'Krämer', 'Mattfeldt', 'Spallek', 'Schneider',
                       'Karaahmetoğlu', 'Saleh', 'Al-Dailami', 'Donth', 'Marc', 'Henning', 'Annalena', 'Ullrich',
                       'Schwabe', 'Muhanad', 'Erich', 'Pohl', 'Zschau', 'Sönke', 'Johann', 'Olaf', 'Ralf', 'Nadja',
                       'Detlef', 'Grötsch', 'Pawlik', 'Oellers', 'Strasser', 'Kristian', 'Kraft', 'Pahlke', 'Annen',
                       'Santos', 'Köhler', 'Gambir', 'Pascal', 'Rimkus', 'Diana', 'Warken', 'Anne', 'Yasmin', 'Hönel',
                       'Bacherle', 'Hennig', 'Robert', 'Alexander', 'Rüdiger', 'Dağdelen', 'Diedenhofen', 'Ludwig',
                       'Enak', 'Janich', 'Otte', 'Rehbaum', 'Sichert', 'Stüwe', 'Krischer', 'Silberhorn',
                       'Stark-Watzinger', 'Peterka', 'Post', 'Gysi', 'Seiter', 'Christine', 'Gastel', 'Jan-Marco',
                       'Seestern-Pauly', 'Tausend', 'Detzer', 'Audretsch', 'Curio', 'Moncsek', 'Notz', 'Gassner-Herz',
                       'Mechthilde', 'Dittmar', 'Angelika', 'Kaiser', 'Beeck', 'Kaddor', 'Schön', 'Simon', 'Thomas',
                       'Esther', 'Kuhle', 'Hess', 'Springer', 'Roloff', 'Willkomm', 'Nico', 'Marie-Agnes',
                       'Castellucci', 'Frei', 'Luiza', 'Nestle', 'Henrichmann', 'Lötzsch', 'Schröder', 'Bilger',
                       'Badum', 'Föhr', 'Joachim', 'Marcel', 'Stamm-Fibich', 'Baradari', 'Sonja', 'Wenzel', 'Töns',
                       'Kathrin', 'Vieregge', 'Lugk', 'Skudelny', 'Jochen', 'Berghegger', 'Grundmann', 'Herbrand',
                       'Takis', 'Glöckner', 'Ulrich', 'Buschmann', 'Radomski', 'Gädechens', 'Dietz', 'Edgar', 'Kipping',
                       'Niels', 'Wolfgang', 'Hagl-Kehl', 'Magwas', 'Janecek', 'Claudia', 'Körber', 'Hauer', 'Deligöz',
                       'Ulrike', 'Britta', 'Holm', 'Weeser', 'Jacobi', 'Lindholz', 'Daniela', 'Jonas', 'Christiane',
                       'Wagenknecht', 'Mieves', 'Stöcker', 'Zierke', 'Sepp', 'Bijan', 'Koß', 'Martina', 'Michael',
                       'Heilmann', 'Brian', 'Daldrup', 'Hierl', 'Zippelius', 'Enrico', 'Slawik', 'Franziska', 'Linda',
                       'De', 'Özoğuz', 'Sorge', 'Krings', 'Vöpel', 'Erik', 'Mittag', 'Ziemiak', 'Ria', 'Perli',
                       'Philipp', 'Sara', 'Schäffler', 'Fahimi', 'Berghahn', 'Gohlke', 'Lucassen', 'Katrin', 'W.',
                       'Grund', 'Latendorf', 'Stegemann', 'Miazga', 'Erhard', 'Mayer', 'Oliver', 'Englhardt-Kopf',
                       'Steinmüller', 'Kassautzki', 'Widmann-Mauz', 'Mario', 'Nina', 'Houben', 'Mascheck', 'Ansgar',
                       'Schisanowski', 'Armin', 'Ana-Maria', 'Al-Halak', 'Harder-Kühnel', 'Stefan', 'Annette',
                       'Jasmina', 'Rosemann', 'Kröber', 'Nicole', 'Tim', 'Rasha', 'Tina', 'Amthor', 'Junge', 'Gunther',
                       'Silke', 'René', 'Herbert', 'Clara', 'Thorsten', 'Trăsnea', 'Timon', 'Pilsinger', 'Straubinger',
                       'Zimmermann', 'Ehrhorn', 'Glaser', 'Ekin', 'Friedhoff', 'Sarah', 'Ortleb', 'Günter', 'Rüddel',
                       'Heck', 'Katharina', 'Spaniel', 'Andrej', 'Krichbaum', 'Hocker', 'Meister', 'Nickholz',
                       'Ophelia', 'Awet', 'Renata', 'Sacher', 'Michel', 'Mark', 'Mijatović', 'Victor', 'Mende', 'Stahr',
                       'Toncar', 'Annegret', 'Eckert', 'Heiligenstadt', 'Sauter', 'Plobner', 'Budde', 'Patricia',
                       'Spahn', 'Gerrit', 'Glogowski-Merten', 'Hagedorn', 'Mariana', 'Bär', 'Agnieszka', 'Mechthild',
                       'Grundl', 'Döring', 'Gitta', 'Gero', 'Gremmels', 'Sabine', 'Renate', 'Rix', 'Klaus-Peter',
                       'Borchardt', 'Hartewig', 'Lahrkamp', 'Färber', 'Frieser', 'Mohamed', 'Gökay', 'Piechotta', 'Ali',
                       'Tabea', 'Witt', 'Radwan', 'Patrick', 'Rupprecht', 'Fechner', 'Hilse', 'Kiziltepe', 'Maximilian',
                       'Hubertus', 'Cornelia', 'Keuter', 'Tesfaiesus', 'Bachmann', 'Ferlemann', 'Winkler', 'Beckamp',
                       'Stumpp', 'Johannes', 'Baum', 'Plum', 'Svenja', 'Heil', 'Luise', 'Helfrich', 'Tilman', 'Schrodi',
                       'Wulf', 'Maja', 'Lütke', 'de', 'Uhl', 'Heitmann', 'Kristine', 'Schwarz', 'Carl-Julius',
                       'Limburg', 'Seif', 'Lamya', 'Marvi', 'Schieder', 'Ariane', 'Föst', 'Christos', 'Metin',
                       'Schnieder', 'Andreas', 'Wirth', 'Gelbhaar', 'Schattner', 'Herbst', 'Jung', 'Manuel', 'Gereon',
                       'Tessa', 'Olav', 'Kasper', 'Kramme', 'Heike', 'Künast', 'Lars', 'Jensen-Bornhöft', 'Münzenmaier',
                       'Carsten', 'Middelberg', 'Petr', 'Emily', 'Helmut', 'Caren', 'Armand', 'Jongen', 'Jan-Niclas',
                       'Banaszak', 'Bleck', 'Cotar', 'Seitz', 'Strengmann-Kuhn', 'Hansjörg', 'Bollmann', 'Rinkert',
                       'Leon', 'Albert', 'Schönberger', 'Udo', 'Lina', 'Wilfried', 'Haug', 'Heinrich', 'Merz',
                       'Carolin', 'Manuela', 'Kießling', 'Braun', 'Volkmar', 'Frauke', 'Hoffmann', 'Winkelmeier-Becker',
                       'Gerschau', 'Julia', 'Christoph', 'Nacke', 'Bystron', 'Aschenberg-Dugnus', 'Hanna', 'Metzler',
                       'Karliczek', 'Joe', 'Linnemann', 'Gabriele', 'Cronenberg', 'Abraham', 'Knoerig', 'Wissing',
                       'Licina-Bode', 'Rief', 'Josef', 'Schätzl', 'Ernst', 'Altmaier', 'Albrecht', 'Jakob', 'Theurer',
                       'Stephan', 'Schwarzelühr-Sutter', 'Sven-Christian', 'Lips', 'Klaus', 'Misbah', 'Vogel',
                       'Manfred', 'Storjohann', 'Moosdorf', 'Frank', 'Bahr', 'Blankenburg', 'Hubertz', 'Swantje',
                       'Kellner', 'Rothfuß', 'Kruse', 'Brehm', 'Grübel', 'Gauland', 'Mann', 'Jörg', 'Lechte', 'Tatti',
                       'Kemmer', 'Cem', 'Staffler', 'Gürpinar', 'Becker', 'Knut', 'Lenz', 'Kober', 'Paula', 'Timo',
                       'Verena', 'Gyde', 'Mützenich', 'Westphal', 'Özdemir', 'Papendieck', 'Amtsberg', 'Catarina',
                       'Melis', 'Hahn', 'Harald', 'Hendrik', 'Florian', 'Lang', 'Volker', 'Otto', 'Keul', 'Fiedler',
                       'Bauer', 'Höchst', 'Omid', 'Matthias', 'Hoppermann', 'Gottfried', 'Lieb', 'Mayer-Lay', 'Brehmer',
                       'Ullmann', 'Sahra', 'Ina', 'Nietan', 'Winklmann', 'Bartol', 'Żaklin', 'Dieter', 'Wiese',
                       'Frohnmaier', 'Luksic', 'Boginski', 'Hennrich', 'Haßelmann', 'Aumer', 'Ronja', 'Farle', 'Amira',
                       'Heidt', 'Brandenburg', 'Altenkamp', 'Derya', 'Wollmann', 'Cansel', 'in', 'Monika',
                       'Göring-Eckardt', 'Brandes', 'Mathias', 'Filiz', 'Corinna', 'Hüppe', 'Nasr', 'Luczak',
                       'Strack-Zimmermann', 'Marlene', 'Birkwald', 'der', 'Mackensen-Geis', 'Hitschler', 'Adler',
                       'Czaja', 'Müller-Gemmeke', 'Oster', 'Tebroke', 'Hellmich', 'Benkstein', 'Klinck', 'Marco',
                       'Völlers', 'Steffen', 'Saathoff', 'Tippelt', 'Kramp-Karrenbauer', 'Christmann', 'Marianne',
                       'Teutrine', 'Weingarten', 'Bartz', 'Hakverdi', 'Pellmann', 'Möhring', 'Aeffner', 'Schierenbeck',
                       'Kotré', 'Klein', 'Bünger', 'Astrid', 'Stracke', 'Michelle', 'Kay-Uwe', 'Funke', 'Teuteberg',
                       'Wissler', 'Rachel', 'Rebecca', 'Maik', 'Bsirske', 'Heidenblut', 'Engelhardt', 'Fäscher',
                       'Leif-Erik', 'Schamber', 'Brugger', 'Leni', 'Mike', 'Katja', 'Bernhard', 'Türk-Nachbaur',
                       'Janssen', 'Lauterbach', 'Albani', 'Hakan', 'Rützel', 'Hartmann', 'Schreiner', 'Baerbock',
                       'Herrmann', 'Klose', 'Carmen', 'Hans-Peter', 'Esdar', 'Benjamin', 'Kai', 'Philippi', 'Grütters',
                       'Dirk-Ulrich', 'Uli', 'Komning', 'Brantner', 'Möller', 'Petry', 'Abel', 'Lambsdorff', 'Lena',
                       'Gerdes', 'Wanderwitz', 'Grau', 'Liebert', 'Katzmarek', 'Kerstin', 'Gründer', 'Wiebke', 'Huber',
                       'Monstadt', 'Antje', 'Roth', 'Machalet', 'Bernstein', 'Anikó', 'Kofler', 'Ricarda', 'Lenders',
                       'Engelhard', 'Sanae', 'Till', 'Mesarosch', 'Kordula', 'Storch', 'Baldy', 'Gesenhues',
                       'Troff-Schaffarzyk', 'Ganserer', 'Anke', 'Reuther', 'Bury', 'Gerster', 'Jürgen', 'Breymaier',
                       'Bettina', 'Paul', 'Michaelsen', 'Peick', 'Weisgerber', 'Malottki', 'Mihalic', 'Wagener',
                       'Yüksel', 'Gehring', 'Müller-Rosentritt', 'Yannick', 'Klüssendorf', 'Kay', 'Lehrieder',
                       'Jurisch', 'Kaufmann', 'Aydan', 'Josephine', 'Ploß', 'Konrad', 'Lindner', 'Seitzl', 'Reinhard',
                       'Kurth', 'Alice', 'Stephanie', 'Schäfer', 'Korte', 'Pau', 'Werner', 'Edelhäußer', 'Reichardt',
                       'Meiser', 'Kiesewetter', 'Emmi', 'Dieren', 'Bodtke', 'Emilia', 'Reginald', 'Dirk', 'Mansoori',
                       'Hagen', 'Beck', 'Weyel', 'Ferschl', 'Uwe', 'Haase', 'Silvia', 'Nicolaisen', 'Lukas', 'Ates',
                       'Ottilie', 'Kopf', 'Juratovic', 'Düring', 'Huy', 'Stegner', 'Sören', 'Reichel', 'Gräßle', 'Jens',
                       'Peggy', 'Djir-Sarai', 'Schielke-Ziesing', 'Anton', 'Träger', 'Dobrindt', 'Bartelt',
                       'Spellerberg', 'Biadacz', 'Baehrens', 'Nouripour', 'Larem', 'Beyer', 'Demir', 'Carina', 'Güler',
                       'Ebner', 'Güntzler', 'Sekmen', 'Kuban', 'Emmerich', 'Dröge']

        self.wordlist = [word for word in self.wordlist if
                         len(word) >= 4 and word not in top100 and word not in abgeordnete]

        # remove nonalphabetical chars
        regex = re.compile('[^a-zA-ZÄÖÜäöüß]')
        self.wordlist = [word for word in self.wordlist if not any(char for char in word if regex.match(char))]
        # self.wordlist = [regex.sub('', item) for item in self.wordlist]

        self.wordlist = [
            word
            for word in self.wordlist
            if word != '' and not word[0].islower() and not (word in german_articles)
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

import fasttext
import fasttext.util  # use pip install fasttext-wheel

# import nltk
import numpy as np

# from nltk.corpus import stopwords


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
    fasttext.util.download_model('de', if_exists='ignore')  # English
    ft = fasttext.load_model('cc.de.300.bin')  # German vocabulary , trained on Wikipedia

    def __init__(self, wordlist):
        self.wordlist = wordlist

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
        # Download the stop words dataset for German
        # nltk.download('stopwords')
        # nltk.download('de')
        # stop_words_german = set(stopwords.words('german'))
        # remove words of lower case and stopwords and the substring "gesetz" and everything after of words
        # we dont want
        # 1. "zur" (kein Nomen, nicht aussagekräftig)
        # 2. "Ist" (auch Füllworter sind manchmal groß geschrieben)
        # 3. "Digitalisierungsgesetesentwurf" -> besser "Digitalisierung"
        # 4. Artikel sind auuch unnöttig
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

        self.wordlist = [
            word.split('gesetz')[0]
            for word in self.wordlist
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
    main()

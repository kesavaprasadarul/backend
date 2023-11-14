import ast  # reading the file

import fasttext.util  # use pip install fasttext-wheel
import numpy as np


# A clas that represents a file and allows querying and analysing its content
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
    ft = fasttext.load_model('cc.de.300.bin')  # German vocabulary , trained on Wikipedia

    def __init__(self, filename):
        with open(filename, 'r') as file:
            self.wordlist = ast.literal_eval(file.read())

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
    def word_families(self):
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


def main():
    # TODO: Text besser einlesen
    # TODO: Ordentliches Preprocessing, zu viele unnötige Wörter
    # cosine similarity (1=same word; 0=completely different word concerning meaning)

    # woerter den versch ressorts zuordnen, Def. ein Wort gehört zu einem Ministerium: die Bezeichnung dieses
    # Ministeriums hat die höchste Prozentuale Ähnlichkeit mit dem Wort (semantisch)

    bundestag_text = WordCounter("ProtokollWords.txt")

    # calculate how often each word appears
    dictionary_counts = bundestag_text.word_count()

    for word, ressort in bundestag_text.word_families().items():
        if dictionary_counts.get(word) > 10:
            print(
                f"Das Wort \"",
                word,
                "\" wurde dem Ministerium für ",
                ressort,
                " zugeordnet und ",
                dictionary_counts.get(word),
                " mal erwähnt.",
            )


if __name__ == "__main__":
    main()

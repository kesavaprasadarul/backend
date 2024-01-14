import os
import re
import shutil

# from nltk.corpus import stopwords
from logging import getLogger

import fasttext  # mypy: ignore
import fasttext.util  # use pip install fasttext-wheel

# import nltk
import numpy as np

from backend.app.core.bundestag_ressorts import BUNDESTAG_RESSORT
from backend.app.core.logging import configure_logging
from backend.app.utils import get_data_folder
from collections import Counter, defaultdict
from backend.app.importer.top_topics_importer.word_blacklists import (
    ABGEORDNETEN_NAMEN,
    TOP_100_NOISE,
    GERMAN_ARTICLES,
    GERMAN_STOPWORDS,
)

from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer

logger = getLogger(__name__)

DEFAULT_STOPWORDS: set[str] = (
    TOP_100_NOISE | ABGEORDNETEN_NAMEN | GERMAN_ARTICLES | GERMAN_STOPWORDS
)


class WordCount:
    def __init__(self, word: str, count: int):
        self.word = word
        self.count = count

    def __str__(self):
        return f"Word: {self.word}, Count: {self.count}"


# A class that represents a file and allows querying and analysing its content
class BertAnalyzer:
    def __init__(self, documents: list[str], stopwords: set[str] = DEFAULT_STOPWORDS):
        self.documents = documents
        self.word_blacklist: set[str] = stopwords

        zero_shot_topic_list = [ressort.value for ressort in BUNDESTAG_RESSORT]

        vectorizer_model = CountVectorizer(stop_words=list(stopwords), ngram_range=(1, 2))
        topic_model = BERTopic(
            language="german",
            verbose=True,
            vectorizer_model=vectorizer_model,
            zeroshot_topic_list=zero_shot_topic_list,
            zeroshot_min_similarity=0.5,
        )

        topics, probs = topic_model.fit_transform(documents)

        ft_model_path = "models/cc.de.300.bin"
        ft_model_path = os.path.join(get_data_folder(), ft_model_path)

        # Download the fasttext model for German if it is not already downloaded
        if not os.path.isfile(ft_model_path):
            logger.info("Downloading fasttext model")
            file_name = fasttext.util.download_model('de', if_exists='ignore')  # English

            logger.info("Moving fasttext model to %s", ft_model_path)

            shutil.move(file_name, ft_model_path)

            if os.path.isfile(file_name + ".gz"):
                os.remove(file_name + ".gz")
        logger.info("Loading fasttext model from %s", ft_model_path)
        self.ft = fasttext.load_model(ft_model_path)  # German vocabulary , trained on Wikipedia

        self.ressort_to_vectors = {
            ressort: self.ft.get_word_vector(ressort.value) for ressort in BUNDESTAG_RESSORT
        }

    # returns the ressort that is most similar to the given word and a dict of all ressorts and their similarity to the word
    def word_to_ressort(
        self, word: str
    ) -> tuple[BUNDESTAG_RESSORT | None, dict[BUNDESTAG_RESSORT, float]]:
        best_ressort: str | None = None
        sim_ressorts = {}
        for res, res_vec in self.ressort_to_vectors.items():
            word_vector = self.ft.get_word_vector(word)
            divisor = np.linalg.norm(word_vector) * np.linalg.norm(res_vec)
            if divisor > 0:
                val = np.dot(word_vector, res_vec) / divisor
                if best_ressort and sim_ressorts[best_ressort] < val:
                    best_ressort = res

                if not best_ressort:
                    best_ressort = res
                sim_ressorts[res] = val
            else:
                sim_ressorts[res] = 0

        return best_ressort, sim_ressorts

    def clean_words(self) -> dict[str, int]:
        # TOP words that appeared at least 20 times (extracted over all protocols of 2023 and 2022), manually verified if they were noise

        word_counter = Counter(self.wordlist)

        # filter blacklist
        word_counter = {
            word: count for word, count in word_counter.items() if word not in self.word_blacklist
        }

        # filter words shorter than 4 chars
        word_counter = {word: count for word, count in word_counter.items() if len(word) >= 4}

        # remove non-alphabetical chars
        word_counter = {word: count for word, count in word_counter.items() if word.isalpha()}

        # remove words with small first letter

        word_counter = {
            word: count for word, count in word_counter.items() if not word[0].islower()
        }

        return word_counter

    def make_word_cloud(self) -> dict[BUNDESTAG_RESSORT, list[tuple[str, int]]]:
        word_counter = self.clean_words()

        ressort_to_words: dict[BUNDESTAG_RESSORT, list[tuple[str, int]]] = defaultdict(list)

        for word, count in word_counter.items():
            ressort, sim_ressorts = self.word_to_ressort(word)

            if ressort:
                ressort_to_words[ressort].append((word, count))
        return ressort_to_words


def main():
    import json
    import unicodedata

    with open(
        'example_docs.json',
        "r",
    ) as f:
        example_documents = json.load(f)

    # with open(
    #     "_SELECT_text_FROM_dip_plenarprotokoll_p_JOIN_dip_plenarprotokoll_202401131120.json",
    #     "r",
    #     encoding='ISO-8859-1',
    # ) as f:
    #     example_documents = json.load(f)
    #     key = list(example_documents.keys())[0]

    #     example_documents = [doc['text'] for doc in example_documents[key]]
    #     for i in range(len(example_documents)):
    #         m_start = re.search(
    #             r'Präsidentin [a-zA-Zä]{5,20} [a-zA-Zä]{3,10}:', example_documents[i]
    #         )
    #         if not m_start:
    #             raise ValueError("Couldn't determine start of text")
    #         example_documents[i] = example_documents[i][m_start.start() :]
    #         example_documents[i] = re.sub(r"\(Beifall .*\)", "", example_documents[i])

    instance = BertAnalyzer(example_documents)
    print("start")
    print(instance.make_word_cloud())


if __name__ == "__main__":
    configure_logging()
    main()

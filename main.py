from tkinter import *

import nltk

nltk.download('punkt')

nltk.download('stopwords')

with open('corpus.txt', 'r', encoding='ISO-8859-1') as f:
    article_data = f.read()


def get_vocabulary(article_data):
    tokens = nltk.word_tokenize(article_data)
    tokens = [token for token in tokens if token.isalnum()]
    tokens = [token.lower() for token in tokens]
    unique_words = set(tokens)
    return unique_words


def split_to_sentences(data):
    sentences = data.split('\n')

    sentences = [sentence.strip() for sentence in sentences]
    sentences = [s for s in sentences if len(s) > 0]

    return sentences


processed_data = split_to_sentences(article_data[0:200000])


def tokenization(sentences):
    tokenized_sentences = []

    for sentence in sentences:
        sentence = sentence.lower()
        tokens = nltk.word_tokenize(sentence)
        tokenized_sentences.append(tokens)
    return tokenized_sentences


vocabulary = get_vocabulary(article_data[0:200000])

processed_data = tokenization(processed_data)


def count_n_grams(corpus, n):
    n_grams = {}

    for sentence in corpus:

        sentence = tuple(sentence)

        for i in range(len(sentence) - n + 1):
            n_gram = sentence[i: i + n]
            n_grams[n_gram] = n_grams.get(n_gram, 0) + 1

    return n_grams


def estimate_probability(current_word, previous_n_gram,
                         n_gram_counts, n_plus1_gram_counts, vocabulary_size, k=1.0):
    previous_n_gram = tuple(previous_n_gram)

    previous_n_gram_count = n_gram_counts.get(previous_n_gram, 0)

    denominator = previous_n_gram_count + k * vocabulary_size

    n_plus1_gram = previous_n_gram + (current_word,)

    n_plus1_gram_count = n_plus1_gram_counts.get(n_plus1_gram, 0)

    numerator = n_plus1_gram_count + k

    probability = numerator / denominator

    return probability


def estimate_probabilities(previous_n_gram, n_gram_counts, n_plus1_gram_counts, vocabulary, k=1.0):
    previous_n_gram = tuple(previous_n_gram)

    vocabulary_size = len(vocabulary)

    probabilities = {}
    for word in vocabulary:
        probability = estimate_probability(word, previous_n_gram,
                                           n_gram_counts, n_plus1_gram_counts,
                                           vocabulary_size, k=k)
        probabilities[word] = probability

    return probabilities


def suggest_words(previous_tokens, n_gram_counts, n_plus1_gram_counts, vocabulary, k=1.0):
    n = len(list(n_gram_counts.keys())[0])

    previous_n_gram = previous_tokens[-n:]

    probabilities = estimate_probabilities(previous_n_gram,
                                           n_gram_counts, n_plus1_gram_counts,
                                           vocabulary, k=k)

    suggestion = []

    probabilities = dict(sorted(probabilities.items(), key=lambda x: x[1], reverse=True))
    i = 0
    for word, prob in probabilities.items():

        suggestion.append(word)
        i += 1
        if i > 8:
            break

    return suggestion


n_gram_counts_list = []

for n in range(1, 6):
    n_model_counts = count_n_grams(processed_data, n)
    n_gram_counts_list.append(n_model_counts)


def get_suggestions(previous_tokens, n_gram_counts_list, vocabulary, k=1.0):
    models = len(n_gram_counts_list)
    suggestion = []
    n = len(previous_tokens)
    for i in range(models - 1):
        if n > i:
            n_gram_counts = n_gram_counts_list[i]
            n_plus1_gram_counts = n_gram_counts_list[i + 1]

            suggestion = suggest_words(previous_tokens, n_gram_counts,
                                       n_plus1_gram_counts, vocabulary,
                                       k=k)

    return suggestion


def check_value(event):
    value = event.widget.get()

    if value != '':
        input_string = value
        input_string = input_string.split()
        data = get_suggestions(input_string, n_gram_counts_list, vocabulary)
        update(data)
    else:
        data = []
        update(data)


def update(data):
    list_box.delete(0, 'end')

    for item in data:
        list_box.insert('end', item)


root = Tk()
root.title('Auto Complete')
root.geometry("400x300")

input_query = Entry(root, width=50, font=('Arial 18'))
input_query.pack(padx=10, pady=10)

input_query.bind('<KeyRelease>', check_value)

list_box = Listbox(root, height=10,
                   width=15,
                   bg="grey",
                   activestyle='dotbox',
                   font="Helvetica",
                   fg="black")

list_box.pack(fill=BOTH)

root.resizable(False, False)

update([])

root.mainloop()

import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from collections import Counter
import gensim
from gensim.corpora import Dictionary
from gensim.models.ldamodel import LdaModel

def generateTopics(url):
    # Retrieve webpage content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove website-specific content such as navigation bars, footers, and advertisements
    for script in soup(["script", "style"]):
        script.decompose()
    for div in soup.find_all('div', class_=lambda x: x != 'article'):
        div.decompose()
    for nav in soup.find_all('nav', class_=lambda x: x != 'article'):
        nav.decompose()
    text = soup.get_text()

    # Preprocess text
    tokens = nltk.word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if not t in stop_words and t.isalpha()]
    lemmatizer = nltk.WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]

    # POS tagging
    pos_tags = nltk.pos_tag(tokens)

    # Named entity recognition
    ner_tags = nltk.ne_chunk(pos_tags)

    # Frequency analysis
    freq_dist = Counter(tokens)

    # LDA topic modeling
    dictionary = Dictionary([tokens])
    corpus = [dictionary.doc2bow([token]) for token in tokens]
    lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=5, passes=20, alpha='auto', eta='auto')

    # Print topics
    print("Topics:")
    topics = lda_model.print_topics(num_topics=5, num_words=10)
    for topic in topics:
        print(topic)

    # Convert topics to a dictionary
    topic_dict = {}
    for topic in topics:
        topic_dict[topic[0]] = [w.split('*')[1].replace('"', '') for w in topic[1].split('+')]

    # Ranking topics by frequency
    topic_freq = {}
    for topic_num, topic_words in topic_dict.items():
        topic_freq[topic_num] = sum([freq_dist[word] for word in topic_words])

    sorted_topics = sorted(topic_freq.items(), key=lambda x: x[1], reverse=True)

    # Get top 5 topics as a list of strings
    top_topics = []
    for topic in sorted_topics[:5]:
        top_topics.append(', '.join(topic_dict[topic[0]]))

    return top_topics

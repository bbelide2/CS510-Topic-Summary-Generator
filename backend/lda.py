import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from collections import Counter
import gensim
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def generateTopics(url):

    print("lda: received request")
    # Retrieve webpage content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove website-specific content such as navigation bars, footers, and advertisements
    for element in soup(["script", "style", "nav", "footer", "aside", "iframe"]):
        element.extract()
    text = soup.get_text()

    # Preprocess text
    tokens = nltk.word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if not t in stop_words and t.isalpha()]

    # Lemmatize tokens
    lemmatizer = nltk.stem.WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]

    # POS tagging
    pos_tags = nltk.pos_tag(tokens)

    # Named entity recognition
    ner_tags = nltk.ne_chunk(pos_tags)

    # Sentiment analysis
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(text)
    sentiment = 'neutral'
    if sentiment_scores['compound'] > 0.1:
        sentiment = 'positive'
    elif sentiment_scores['compound'] < -0.1:
        sentiment = 'negative'

    # Frequency analysis
    freq_dist = Counter(tokens)

    # LDA topic modeling
    dictionary = Dictionary([tokens])
    corpus = [dictionary.doc2bow([token]) for token in tokens]
    lda_model = LdaModel(corpus, id2word=dictionary, num_topics=5)
    topics = lda_model.show_topics(num_topics=5, num_words=10, formatted=False)

    print("topics: ")
    print(topics)

    # Refine topics based on sentiment
    topic_dict = {}
    for topic in topics:
        topic_dict[topic[0]] = [w[0] for w in topic[1]]
    if sentiment == 'positive':
        topic_dict = {k: v for k, v in topic_dict.items() if 'good' in v or 'great' in v or 'excellent' in v}
    elif sentiment == 'negative':
        topic_dict = {k: v for k, v in topic_dict.items() if 'bad' in v or 'poor' in v or 'terrible' in v}

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

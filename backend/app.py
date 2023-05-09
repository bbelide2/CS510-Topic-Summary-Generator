import os
import json
from lda import *
from flask_cors import CORS

import openai
from flask import Flask, redirect, render_template, request, url_for, jsonify

app = Flask(__name__)
CORS(app)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=['POST'])
def index():
    print("received request")

    # extract url from request
    url = request.get_data().decode('utf-8')
    print(url)
    url = json.loads(url)
    url = url["url"]

    # use LDA to get top topics
    print("calling lda")
    topics_from_lda = generateTopics(url)
    print(topics_from_lda)
    print("done calling lda")

    # call openAI for summaries
    pr = generate_prompt_topics(topics_from_lda, url)
    print(pr)
    response1 = openai.Completion.create(
        model="text-davinci-003",
        prompt=pr,
        temperature=0.1,
        max_tokens=3800
    )

    # get related links by calling openAI
    pr = generate_prompt_related_links(url)
    print(pr)
    response2 = openai.Completion.create(
        model="text-davinci-003",
        prompt=pr,
        temperature=0.1,
        max_tokens=3800
    )

    response = {
        "result": response1.choices[0].text + "\n" + response2.choices[0].text

    }
    print(response)
    return jsonify(response), 200

def generate_prompt_related_links(url):
    return """Generate related links and resources list for the content in this webpage: {}
""".format(url)

def generate_prompt_topics(words, url):
    return """Generate top 5 topics (topic name as a string) from this webpage: {}, where each topic is generated from the keywords present in this list : {}. Each entry in this list contains the top words for each topic. Also generate summaries for each topic in the webpage
""".format(url, words)

def generate_prompt(link):
    return """Generate top topics in this web page along with their brief summaries: {}
""".format(link)

if __name__ == "__main__":
    print("started")
    app.run(host='0.0.0.0',port=8000)

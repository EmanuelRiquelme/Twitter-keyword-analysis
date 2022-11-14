from transformers import pipeline
import numpy as np

specific_model = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")

def Sentiment(tweets):
    output_model = specific_model(tweets.tolist())
    labels = ["NEG","NEU","POS"]
    idx = []
    for output in output_model:
        idx.append(labels.index(output["label"])-1)
    return np.array(idx)


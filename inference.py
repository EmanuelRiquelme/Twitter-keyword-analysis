from keybert import KeyBERT
from sen_model import Sentiment
from sampling import sampling_inference
import torch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplcyberpunk
from adjustText import adjust_text
class Keyword_oracle():
    def __init__(self,file_name,
                    weight_rt_fav = [1,4],
                    noise_threshold = 75,
                    words_exp = ["user","http","rt","fav",'https'],
                    **kwargs
                ):
            self.key_bert = KeyBERT()
            self.file_name = file_name
            self.keybert_args = kwargs
            self.weight_rt_fav =  weight_rt_fav
            self.raw_tweets= sampling_inference(file_name).sampled_df()
            self.noise_threshold = noise_threshold if kwargs['top_n'] == 1 else 90 if kwargs['top_n'] == 2 else 95 
            self.tweets = self.raw_tweets['Tweet']
            self.retweet = self.raw_tweets['Retweet']
            self.favs = self.raw_tweets['Favs']
            self.sentiment_eval = self.__sentimient_eval__()
            self.words_exp = words_exp
            self.mined_tweets = self.__tweets_mined__()
            self.denoised_df = self.__denoised_df__()
            self.percentiles = self.__find_threshold__()
            self.categorical = self.__categorical__()

    def __sentimient_eval__(self):
        return Sentiment(self.tweets)

    def __tweets_mined__(self):
        raw_keywords = self.key_bert.extract_keywords(self.tweets,
               keyphrase_ngram_range = self.keybert_args['keyphrase_ngram_range'],
                diversity = self.keybert_args['diversity'],
                top_n = self.keybert_args['top_n']
                )
        key_words,engagement,acum_sents = [],[],[]
        for keys,retweet,fav,sent in zip(raw_keywords,self.retweet,self.favs,self.sentiment_eval):
            for key in keys:
                if not set(key[0].split()).intersection(set(self.words_exp)):
                    key_words.append(key[0])
                    engagement.append(1+retweet/self.weight_rt_fav[0]+fav/self.weight_rt_fav[1])
                    acum_sents.append(sent+retweet/self.weight_rt_fav[0]*(sent)+fav/self.weight_rt_fav[1]*sent)
        key_word_data = {
            "Key": key_words,
            'engagement': engagement,
            'emotions overall':acum_sents
            }
        return pd.DataFrame(key_word_data).groupby(['Key'], as_index=False).sum()


    def __denoised_df__(self):
        df = self.mined_tweets
        tweets = df['engagement']
        percentile =  np.percentile(tweets, self.noise_threshold)
        return df[tweets > percentile].reset_index(drop=True)

    def __find_threshold__(self):
        df = self.mined_tweets
        tweets = df['emotions overall']
        top_threshold = self.noise_threshold
        bottom_threshold = 100-top_threshold
        while np.percentile(tweets,top_threshold) <= 0 and np.percentile(tweets,100-top_threshold):
            try:
                top_threshold +=5
                bottom_threshold -= 5
            except top_threshold == 95: 
                top_threshold,bottom_threshold = 0,0
        bottom_threshold,top_threshold = np.percentile(tweets,bottom_threshold),np.percentile(tweets,top_threshold)
        return bottom_threshold,top_threshold
    def __categorical__(self):
        df = self.denoised_df
        tweets = df['emotions overall'].to_numpy()
        categorical = ['neutral','positive','negative']
        bottom_threshold,top_threshold = self.percentiles
        pos = (tweets >= top_threshold) if top_threshold > 0 else np.zeros(tweets.shape[0])
        neg = (tweets <= bottom_threshold)*-1 if bottom_threshold < 0 else np.zeros(tweets.shape[0])
        numerical = pos+neg
        return [categorical[index] for index in numerical.astype(int)]
    
    def return_table(self):
        self.denoised_df['Categorical'] = self.__categorical__()
        return self.denoised_df.sort_values(by=['emotions overall'],ascending = False).reset_index(drop=True)

    def plot(self):
        df = self.denoised_df
        plt.style.use("cyberpunk")
        keys = df['Key']
        x,y = df['engagement'],df['emotions overall']
        fig, ax = plt.subplots()
        ax.scatter(x, y)
        text = [plt.text(x_value,y_value,key_value) for x_value,y_value,key_value in zip(x,y,keys)]
        adjust_text(text)
        bottom_threshold,top_threshold =  self.percentiles
        plt.axhline(bottom_threshold ,c= "red", marker='.', linestyle=':') if bottom_threshold < 0 else None 
        plt.axhline(top_threshold,c= "magenta", marker='.', linestyle=':') if top_threshold > 0 else None
        plt.title(f"Denoised sentiment analysis of {self.file_name}")
        plt.xlabel("Engagement")
        plt.ylabel("Emotions Overall")
        return fig

if __name__ == "__main__":
    file_name ='Graham Potter'
    Keyword_oracle = Keyword_oracle(file_name,
                                    keyphrase_ngram_range = (1,2),
                                    diversity=0.3,top_n=3)
    Keyword_oracle.plot()
    print(Keyword_oracle.return_table())

import random
import pandas as pd
import numpy as np
import scipy.stats
np.set_printoptions(suppress=True)

class sampling_inference():
    def __init__(self,file_name,weight = [1,4]):
        self.raw_tweets= pd.read_excel(f"sheets/{file_name}.xlsx")
        self.weight = weight
        self.engagement = self.__engagement__()
        self.perc = self.__eval_perc__()
        self.perc_thres = np.percentile(self.engagement,self.perc)
    def __engagement__(self):
        tweets = self.raw_tweets['Tweet']
        raw_retweets = self.raw_tweets['Retweet'].to_numpy()
        raw_favs = self.raw_tweets['Favs'].to_numpy()
        engagement = raw_retweets/self.weight[0]+raw_favs/self.weight[1]
        return engagement 
    def __eval_perc__(self,perc=75):
        engagement = self.engagement
        while np.percentile(engagement,perc) == 0 and perc < 95:
            perc += 5
        return perc
    def sampled_df(self):
        engagement = self.engagement
        above_perc = np.where(self.engagement >= self.perc_thres)[0]
        bellow_perc = np.where(self.engagement < self.perc_thres)[0].tolist()
        bellow_perc = np.array(random.sample(bellow_perc,above_perc.shape[0]))
        sampled_rows = np.concatenate((above_perc,bellow_perc))
        sampled_df= self.raw_tweets.loc[sampled_rows].reset_index(drop=True)
        del sampled_df['Unnamed: 0']
        return sampled_df


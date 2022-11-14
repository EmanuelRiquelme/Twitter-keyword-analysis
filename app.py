import streamlit as st
from inference import Keyword_oracle
from datetime import date
from extract_tweets import extract_tweets
import torch
import gc
from pathlib import Path


header = st.container()
get_tweet= st.container()
features= st.container()
modelTraining = st.container()



with get_tweet:
    Path('sheets/').mkdir(exist_ok=True)
    st.header("Place the topic you want to research on Twitter :bird:")
    input_keyword =  st.text_input('Write the keyword:')
    if input_keyword:
        current_date = date.today()
        data_since = st.date_input('from which date:',current_date)
        data_until = st.date_input('until which date:',current_date)
        max_kw = st.slider('maximum words per keyword', 1, 3, 1)
        st.text('This process may take a few seconds')
        st.text(f'plot of the keywords asociated with the topic {input_keyword}:')
        extract_tweets(input_keyword,data_since,data_until)
        oracle = Keyword_oracle(input_keyword,
                                        keyphrase_ngram_range = (1,max_kw),
                                        diversity=0.3,top_n=3)
        st.pyplot(oracle.plot())
        st.text("Table of the most popular keywords")
        table = oracle.return_table()
        st.dataframe(table)
        st.download_button(
            label="Download data as CSV",
            data= table.to_csv().encode('utf-8'),
            file_name= f'{input_keyword}.csv',
            mime='text/csv',
        )
        del oracle

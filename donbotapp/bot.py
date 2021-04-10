import os, io
import errno
import urllib
import urllib.request
import hashlib
import re
import requests
from time import sleep
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import pandas as pd
from ast import literal_eval
from cdqa.utils.filters import filter_paragraphs
from cdqa.utils.download import download_model, download_bnpp_data
from cdqa.pipeline.cdqa_sklearn import QAPipeline
from cdqa.utils.converters import pdf_converter

def crawl_result_urls(slugify_keyword):
    req = Request('https://google.com/search?q=' + slugify_keyword, headers={'User-Agent': 'Mozilla/5.0'})                                
    html = urlopen(req).read()
    bs = BeautifulSoup(html, 'html.parser')
    results = bs.find_all('div', class_='ZINbbc')
    result_urls=[]
    try:
        for result in results:
            try:
                link = result.find('a')['href']
                print(link)
            except:
                continue
            if 'url' in link:
                result_urls.append(re.search('q=(.*)&sa', link).group(1))
    except (AttributeError, IndexError) as e:
        pass
    return result_urls 
def get_result_details(url):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        bs = BeautifulSoup(html, 'html.parser')
        try:
            title =  bs.find(re.compile('^h[1-6]$')).get_text().strip().replace('?', '').lower()
            # Set your path to pdf directory
            filename = "pdf_folder/" + title + ".pdf"
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise
            with open(filename, 'w') as f:
                for line in bs.find_all('p')[:5]:
                    f.write(line.text + '\n')
        except AttributeError:
            pass
    except urllib.error.HTTPError:
        pass
def find_answer(question):
    # Set your path to pdf directory
    df = pdf_converter(directory_path='pdf_folder/')
    cdqa_pipeline = QAPipeline(reader='models/bert_qa.joblib')
    cdqa_pipeline.fit_retriever(df)
    query = question + '?'
    prediction = cdqa_pipeline.predict(query)

    # print('query: {}\n'.format(query))
    # print('answer: {}\n'.format(prediction[0]))
    # print('title: {}\n'.format(prediction[1]))
    # print('paragraph: {}\n'.format(prediction[2]))
    return prediction[0]


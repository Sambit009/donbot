from django.shortcuts import render
from django.views import View
import urllib
from time import sleep
from .bot import crawl_result_urls,find_answer,get_result_details
# Create your views here.
class Index(View):
    def get(self,request):
        return render(request,'index.html')

    def post(self,request):
        question = request.POST['question']
        print(question)
        slugify_keyword = urllib.parse.quote_plus(question)
        print(slugify_keyword)
        result_urls = crawl_result_urls(slugify_keyword)
        for url in result_urls[:3]:
            get_result_details(url)
            sleep(5)
        answer = find_answer(question)
        print('Answer: ' + answer)
        return render(request,'index.html',{'answer':answer})

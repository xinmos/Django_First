from django.shortcuts import render
from django.http import JsonResponse
from backend.Spider import Spider
import os
import json

def ajaxRe(request):
    # city = '大连'
    city = request.GET.get('city')
    spider = Spider(city)
    data = {
        'ret': True,
        'dict': {
            'sightList': spider.getList(),
        }
    }
    #解决中文乱码
    return JsonResponse(data, json_dumps_params={'ensure_ascii':False})

def index(request):
    return render(request, 'index.html')

def city(request):
    DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fileName = 'templates/js/city.json'
    f = open(os.path.join(DIR, fileName), 'r', encoding='utf-8')
    data = json.load(f)
    f.close()
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

def detail(request):
    DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fileName = 'templates/js/detail.json'
    f = open(os.path.join(DIR, fileName), 'r', encoding='utf-8')
    data = json.load(f)
    f.close()
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

def home(request):
    DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fileName = 'templates/js/index.json'
    f = open(os.path.join(DIR, fileName), 'r', encoding='utf-8')
    data = json.load(f)
    f.close()
    return JsonResponse(data, json_dumps_params={'ensure_ascii':False})
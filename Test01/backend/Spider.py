import os
import time
import json
import difflib
import random
import requests

# 爬虫类
class Spider:
    qunarList = []
    tongcList = []
    tuniuList = []
    proxies = []
    headers = []
    city = ''
    # 私有属性
    __DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    def __init__(self, city):
        self.city = city
        self.proxies = [
            '59.42.42.96:8118',
            '113.121.21.236:9999',
            '175.44.152.140:9000',
            '222.89.32.136:9999',
            '163.204.242.96:9999',
            '1.197.203.194:9999'
        ]
        self.headers = [
            'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5',
            'Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5',
            'MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
            'NOKIA5700/ UCWEB7.0.2.37/28/999',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)'
        ]
        self.fileVerify()

    # 爬取去哪儿数据
    def qunar(self):
        url = 'http://touch.piao.qunar.com/touch/list.json'
        params = {
            'region': self.city,
            'isForeign': 'false',
            'page': 1,
            'pageSize': 100,
            'keyword': '景点门票'
        }
        response = requests.get(url, params=params)
        sightList = response.json()['data']['sightList']
        newList = []
        for sight in sightList:
            newPriceList = []
            for price in sight['priceList']:
                priceJson = {
                    'productName': price['productName'],
                    'qunarPrice	': price['qunarPrice'],
                    # 景点详细信息地址
                    'productDetailScheme': "https:" + price['productDetailScheme'],
                }
                newPriceList.append(priceJson)
            if 'sightSimpleDesc' not in sight:
                sight['sightSimpleDesc'] = ''
            newjson = {
                'id': sight['id'],
                'imgURL': sight['imgURL'],
                'name': sight['name'],
                'qunarPrice': sight['qunarPrice'],
                'sightSimpleDesc': sight['sightSimpleDesc'],
                'priceList': newPriceList
            }
            newList.append(newjson)
        self.qunarList = newList
        self.saveFile(newList, 'qu.json')

    # 爬取同程数据
    def tongc(self):
        pageNo = 1
        url = url = 'https://m.ly.com/scenery/json/scenerynearycitylist.html'
        params = {
            'page': pageNo,
            'keyword': self.city
        }
        newList = []
        while pageNo < 10:
            response = requests.get(url, params=params, headers={'User-Agent': random.choice(self.headers)}, proxies={'http': random.choice(self.proxies)})
            for res in response.json()['sceneryinfo']:
                newList.append(res)
            pageNo = 1 + pageNo
            time.sleep(1)
        for tong in newList:
            newJson = {
                'name': tong['name'],
                'amount': tong['amount'],
                'href': tong['href'],
                'summary': tong['summary'],
            }
            self.tongcList.append(newJson)
        self.saveFile(self.tongcList, 'to.json')

    # 爬去途牛数据
    def tuniu(self):
        url = 'https://m.tuniu.com/m2015/mpChannel/searchInfoAjax?d={"page": 1, "limit": 100, "keyword": '+ self.city +', "location": []}'
        params = {
            'd': json.dumps({
                "page": 1,
                "limit": 100,
                "keyword": self.city,
                "location": []
            })
        }
        newList = []
        response = requests.get(url, params=params, headers={'User-Agent': random.choice(self.headers)}, proxies={'http': random.choice(self.proxies)})
        sightList = response.json()['data']['list']
        for sight in sightList:
            newJson = {
                'id': sight['id'],
                'name': sight['name'],
                'salePrice': sight['salePrice']
            }
            newList.append(newJson)
        self.tuniuList = newList
        self.saveFile(newList, 'tu.json')

    # 验证文件是否存在
    def fileVerify(self):
        try:
            fileName1 = 'templates/js/' + self.city + 'qu.json'
            f1 = open(os.path.join(self.__DIR, fileName1), 'r', encoding='utf-8')
            qunarData = json.load(f1)
            self.qunarList = qunarData['data']
            f1.close()
        except IOError:
            self.qunar()
        try:
            fileName2 = 'templates/js/' + self.city + 'to.json'
            f2 = open(os.path.join(self.__DIR, fileName2), 'r', encoding='utf-8')
            tongcData = json.load(f2)
            self.tongcList = tongcData['data']
            f2.close()
        except IOError:
            self.tongc()
        try:
            fileName3 = 'templates/js/' + self.city + 'tu.json'
            f3 = open(os.path.join(self.__DIR, fileName3), 'r', encoding='utf-8')
            tuniuData = json.load(f3)
            self.tuniuList = tuniuData['data']
            f3.close()
        except IOError:
            self.tuniu()

    # 保存文件到本地
    def saveFile(self, newList, suffix):
        fileName = 'templates/js/' + self.city + suffix
        newJson = {
            'ret': True,
            'data': newList
        }
        with open(os.path.join(self.__DIR, fileName), 'w', encoding='utf-8') as f:
            f.write(json.dumps(newJson, ensure_ascii=False))

    # 处理数据给后台
    def getList(self):
        for sight in self.qunarList:
            for item in self.tuniuList:
                if self.string_similar(sight['name'],item['name']) > 0.6:
                    sight['tuniuPrice'] = item['salePrice']
                else:
                    continue
            for item2 in self.tongcList:
                if self.string_similar(sight['name'], item2['name']) > 0.6:
                    sight['tongcPrice'] = item2['amount']
                else:
                    continue
            if 'tuniuPrice' not in sight:
                sight['tuniuPrice'] = '无数据'
            if 'tongcPrice' not in sight:
                sight['tongcPrice'] = '无数据'
        return self.qunarList

    # 比较文本相似度
    def string_similar(self, s1, s2):
        return difflib.SequenceMatcher(None, s1, s2).quick_ratio()
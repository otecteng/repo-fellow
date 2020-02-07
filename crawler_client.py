import json
import organization
import requests
from   requests_html import HTMLSession
import json

class CrawlerClient:
    def __init__(self,site,token,data_path = "./data"):
        self.site = site
        self.token = token
        self.session = HTMLSession()
        self.data_path = data_path

    def getSingleResource(self,url):
        query = self.site + url 
        print(query)
        response = self.session.get(url = query, timeout = 20)
        if response.status_code > 300:
            print("Error {} to open {}".format(response.status_code,query))
        return response.json()

    def getResource(self,url,limit = None):
        page,recordsPerPage = 1, 50
        data = []
        while True:
            if limit is not None and len(data) >= limit :
                break
            query = self.site + url + "&page={}&per_page={}".format(page,recordsPerPage)
            print(query)
            response = self.session.get(url = query, timeout = 20)
            if response.status_code > 300:
                print("Error {} to open {}".format(response.status_code,query))
                break
            ret = response.json()
            data = data + ret
            page = page + 1
            if(len(ret) < recordsPerPage):
                break
        return data
# -*- coding: utf-8 -*-
import json
import urllib.request as request
import os

def handleEsim():
    urlad = "http://172.16.139.92:8201/_cat/indices?h=index"
    req = request.Request(urlad)
    #req.add_header('Content-Type', 'application/json')
    response = request.urlopen(req)
    print(response)


from elasticsearch import Elasticsearch
from datetime import datetime

def handleEsim2():
    es = Elasticsearch(hosts="http://10.16.238.103:8200")
    for line in open("C:\\Users\\ay05\\Desktop\\new_e11.txt"):
        #print(es.search(index=line, body={"query": {"match_all": { }}}))
        #test(line)
        line = line.strip('\n')
        creation_date = test(line)
        print(creation_date)
        body ={"index": line, "creation_date": creation_date, "location": "E11"}
        es.index(index='index_create_date_e11', doc_type='_doc', body=body, id=None)

def test(indexname):
    req = request.Request("http://172.16.139.99:8201/"+indexname+"/_settings/index.creation_date")
    req.add_header('Content-Type', 'application/json')
    response = request.urlopen(req)
    jsonBody = json.loads(response.read())
    creation_date = jsonBody[indexname]["settings"]["index"]["creation_date"]
    return creation_date

if __name__ == '__main__':
    #test()
    handleEsim2()
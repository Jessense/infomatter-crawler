from flask import Flask, Response
from flask import request
import re
from bs4 import BeautifulSoup
import requests
import json

from weibo_crawler import *
from gas_crawler import *
from zhihu_crawler import *

app = Flask(__name__)



@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/weibo', methods=['GET'])
def search_weibo():
    if request.method == 'GET':
        keyword = request.args.get('keyword', '')
        return Response(weibo(keyword), mimetype='application/json')


@app.route('/wechat', methods=['GET'])
def search_wechat():
    if request.method == 'GET':
        keyword = request.args.get('keyword', '')
        return Response(wechat_wasi(keyword), mimetype='application/json')


@app.route('/zhihu', methods=['GET'])
def zhihu_activity():
    if request.method == 'GET':
        keyword = request.args.get('keyword', '')
        return Response(zhihu_crawler(keyword), mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

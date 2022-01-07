# -*- coding: utf-8 -*-
from scrapy import Spider, Request
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, csv, json

class xxlhorecaSpider(Spider):
    name = "xxlhoreca1"
    start_urls = ['https://www.xxlhoreca.com/nl/']

    use_selenium = False
    count = 0
    reload(sys)
    sys.setdefaultencoding('utf-8')

    f1 = open('Missing_Order_IDs part4.csv')
    csv_items = csv.DictReader(f1)
    first_item = None
    keys = csv_items.fieldnames
    models = []
    for i, row in enumerate(csv_items):
        models.append(row)
    f1.close()

    def parse(self, response):
        for row in self.models:
            id = row.values()[2]
            url = 'https://www.xxlhoreca.com/nl/search/{}/page1.ajax?limit=10&sort=popular'.format(id.replace('#', '%23').replace(' ', '+'))

            yield Request(url, self.parse_products)

    def parse_products(self, response):
        data = json.loads(response.body)
        if len(data['products']) > 0:
            url = data['products'][0]['url']
            yield Request(url, callback=self.parse_product)


    def parse_product(self, response):
        self.count += 1
        print self.count
        item = OrderedDict()

        attr_trs = response.xpath('//div[@class="usp-block"]/table//tr')
        Art_Nr = ''
        brand = ''
        guarantee = ''
        for tr in attr_trs:
            key = ''.join(tr.xpath('./td[1]//text()').extract())
            val = ''.join(tr.xpath('./td[2]//text()').extract())
            if 'Artikelnummer' in key:
                Art_Nr = val
            elif 'Merk' in key:
                brand = val
            elif 'Garantie' in key:
                guarantee = val

        item['Art_Nr'] = Art_Nr
        item['Brand'] = brand
        item['Name'] = response.xpath('//h1[@class="product-title"]/text()').extract_first()

        categories = response.xpath('//span[@class="xxl-breadcrumb"]/a/text()').extract()
        for i in range(4):
            item['Category_' + str(i+1)] = ''
        for i, cat in enumerate(categories):
            if i > 3: break
            item['Category_' + str(i+1)] = cat

        price_old = response.xpath('//span[@class="old-price"]/text()').extract_first()
        new_price = response.xpath('//span[@class="new-price-ex"]/text()').extract_first()
        if new_price:
            new_price = new_price.strip()
        btw_price = response.xpath('//span[@class="new-price-in"]/text()').extract_first()
        item['Price_Old'] = price_old
        item['Price_New'] = new_price
        item['Price_VAT'] = btw_price
        item['Guarantee'] = guarantee
        item['Url'] = response.url

        yield item
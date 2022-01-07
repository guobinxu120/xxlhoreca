# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, json

class dekbedSpider(Spider):
    name = "bol_dekbedovertrekken"
    start_urls = ['https://www.bol.com/nl/l/dekbedovertrekken/N/14194/?view=list&origin=8', 'https://www.bol.com/nl/l/kinderdekbedovertrekken/N/30372/?view=list&origin=8']

    use_selenium = True
    count = 0
    reload(sys)
    sys.setdefaultencoding('utf-8')


    def parse(self, response):
        products = response.xpath('//li[@itemprop="itemListElement"]/meta[@itemprop="url"]/@content').extract()
        if not products:
            products = response.xpath('//a[@class="product-image product-image--list"]/@href').extract()
            if not products:
                products = response.xpath('//a[@class="hit-area-listpage hit-area__link"]/@content').extract()
                if not products:
                    pass

        for i, url in enumerate(products):

            yield Request(response.urljoin(url), self.parse_option)
            # break
        next = response.xpath('//li[contains(@class,"pagination__controls pagination__controls--next")]/a/@href').extract_first()
        if next:
            # time.sleep(0.5)
            url = response.urljoin(next)+'&view=list'
            yield Request(url, callback=self.parse)

    def parse_option(self, response):
        option_tags = response.xpath('//div[@class="feature-options feature-options--btns"]/a/@href').extract()
        if option_tags:
            for option_tag in option_tags:
                # time.sleep(0.5)
                yield Request(option_tag, self.finalParse)
        else:
            item = OrderedDict()
            item['Brand'] = response.xpath('//a[@data-role="BRAND"]/text()').extract_first()
            item['Name'] = response.xpath('//h1[@data-test="title"]/text()').extract_first()
            item['Url'] = response.url
            try:
                rating = response
                item['Rating'] = response.xpath('//span[@class="rating-stars__value"]/span/span/text()').extract_first()
            except:
                item['Rating'] = ''
            #
            item['Reviews'] = response.xpath('//a[@title="reviews"]/span/text()').extract_first()

            oldprices = response.xpath('//div[@data-dbk-product-summary]//span[contains(@class,"dbk-price_old")]/text()').re(r'[\d,.]+')
            oldprice = 0.0
            if oldprices:
                oldprice = float(oldprices[0].replace('.', '').replace(',', '.'))

            oldprices = ''.join(response.xpath('//div[@data-test="default-buy-block"]//*[@data-test="price"]//text()').extract()).replace('-', '').replace(',', '.').replace(' ', '').strip()
            if oldprices and oldprices[-1] == '.':
                price = oldprices + '0'
                item['price'] = price

            attrs = response.xpath('//ul[@class="product-small-specs product-small-specs--large"]/li/text()').extract()
            item['Materiaal'] = attrs[0].strip()
            item['maat_option'] = attrs[1].strip()
            item['Delivery'] = ''.join(response.xpath('//div[@data-test="delivery-info"]/text()').extract()).strip()

            datas = response.xpath('//ul[@class="buy-block__usps check-list--succes check-list--usps"]/li')
            for li_data in datas:
                strdata = ' '.join(li_data.xpath('.//text()').extract())
                if 'Gratis'  in strdata:
                    item['Gratis'] = strdata

            spec_titles = response.xpath('//dl[@class="specs__list"]/dt[@class="specs__title"]/text()').extract()
            spec_vals = response.xpath('//dl[@class="specs__list"]/dd[@class="specs__value"]/text()').extract()
            for i, title in enumerate(spec_titles):
                if 'Type instopstrook' in title:
                    item['Type instopstrook'] = spec_vals[i].strip()
            yield item



    def finalParse(self, response):
        try:
            item = OrderedDict()
            item['Brand'] = response.xpath('//a[@data-role="BRAND"]/text()').extract_first()
            item['Name'] = response.xpath('//h1[@data-test="title"]/text()').extract_first()
            item['Url'] = response.url
            try:
                rating = response
                item['Rating'] = response.xpath('//span[@class="rating-stars__value"]/span/span/text()').extract_first()
            except:
                item['Rating'] = ''
            #
            item['Reviews'] = response.xpath('//a[@title="reviews"]/span/text()').extract_first()

            oldprices = response.xpath('//div[@data-dbk-product-summary]//span[contains(@class,"dbk-price_old")]/text()').re(r'[\d,.]+')
            oldprice = 0.0
            if oldprices:
                oldprice = float(oldprices[0].replace('.', '').replace(',', '.'))

            oldprices = ''.join(response.xpath('//div[@data-test="default-buy-block"]//*[@data-test="price"]//text()').extract()).replace('-', '').replace(',', '.').replace(' ', '').strip()
            if oldprices and oldprices[-1] == '.':
                price = oldprices + '0'
                item['price'] = price

            attrs = response.xpath('//ul[@class="product-small-specs product-small-specs--large"]/li/text()').extract()
            item['Materiaal'] = attrs[0].strip()
            item['maat_option'] = attrs[1].strip()
            item['Delivery'] = ''.join(response.xpath('//div[@data-test="delivery-info"]/text()').extract()).strip()

            datas = response.xpath('//ul[@class="buy-block__usps check-list--succes check-list--usps"]/li')
            for li_data in datas:
                strdata = ' '.join(li_data.xpath('.//text()').extract())
                if 'Gratis'  in strdata:
                    item['Gratis'] = strdata

            spec_titles = response.xpath('//dl[@class="specs__list"]/dt[@class="specs__title"]/text()').extract()
            spec_vals = response.xpath('//dl[@class="specs__list"]/dd[@class="specs__value"]/text()').extract()
            for i, title in enumerate(spec_titles):
                if 'Type instopstrook' in title:
                    item['Type instopstrook'] = spec_vals[i].strip()
            yield item



        except Exception as e:
            print e.message


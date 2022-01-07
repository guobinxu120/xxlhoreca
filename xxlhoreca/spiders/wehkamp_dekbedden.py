# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, json

class dekbedSpider(Spider):
    name = "wehkamp_dekbedden"
    # start_urls = ['https://www.wehkamp.nl/wonen-slapen/beddengoed/dekbedovertrekken/C28_8H3_H30/']
    start_urls = ['https://www.wehkamp.nl/wonen-slapen/beddengoed/dekbedden/C28_8H3_H27/']

    use_selenium = False
    count = 0
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse, meta={'page':1})
    def parse(self, response):
        products = response.xpath('//a[@class="l-article-card"]/@href').extract()
        for i, url in enumerate(products):
            # url = product.xpath('./div/a/@href').extract_first()
            yield Request(url, self.finalParse, dont_filter=True)
            # break
        # page = response.meta['page']
        # if page < 2:
        #
        #     url = response.urljoin(next)
        #     yield Request(url, callback=self.parse)

    # def parse_option(self, response):
    #     option_tags = response.xpath('//select[@id="product-variants"]/option')
    #     for option_tag in option_tags:
    #         id = option_tag.xpath('./@value').extract_first()
    #         variant = option_tag.xpath('./text()').extract_first()
    #         disabled = option_tag.xpath('./@disabled')
    #         if not disabled:
    #             if id:
    #                 url = response.url+ '?id={}'.format(id)
    #                 yield Request(url, self.finalParse, meta={'variant':variant}, dont_filter=True)
    #             else:
    #                 yield Request(response.url, self.finalParse, meta={'variant':variant}, dont_filter=True)

    def finalParse(self, response):
        item = OrderedDict()
        item['name'] = response.xpath('//span[contains(@class,"pdp-product--title")]/text()').extract_first()
        item['brand'] = response.xpath('//span[contains(@class,"pdp-product--brand")]/text()').extract_first()
        item['url'] = response.url
        # try:
        #     rating = response.body.split('ratingValue')[-1].split(',')[0].replace('"', '')
        #     item['Rating'] = rating
        # except:
        item['rating'] = response.xpath('//span[@class="average"]/text()').extract_first()
        item['reviews'] = response.xpath('//span[@class="count"]/text()').extract_first()

        oldprices = response.xpath('//div[contains(@class,"pdp-price")]/span[contains(@class, "margin-right-xsmall")]/text()').re(r'[\d,.]+')
        oldprice = None
        if oldprices:
            oldprice = float(oldprices[0])
        item['old_price'] = oldprice

        oldprices = response.xpath('//div[contains(@class,"pdp-price")]/strong/span[contains(@class, "position-relative")]/text()').re(r'[\d,.]+')
        price = None
        if oldprices:
            price = float(oldprices[0])
        item['price'] = price
        item['delivery'] = response.xpath('//span[@class="pdp-delivery--value"]/text()').extract_first()

        item['Boxspring'] = ''
        item['Garantie'] = ''
        item['Maximale belasting'] = ''
        attrs = response.xpath('//table[@class="specifications__table"]//tr')
        for tr in attrs:
            key = tr.xpath('./th/text()').extract_first()
            val = tr.xpath('./td/text()').extract_first()
            if 'vulling' == key:
                item['vulling'] = val
            elif 'Vulgewicht (gr/m2)' == key:
                item['Vulgewicht (gr/m2)'] = val
            elif 'tijk' in key:
                item['tijk'] = val
        try:
            jsondata = json.loads(response.body.split('"items":')[1].split('}]}')[0]+'}]')
            for option in jsondata:
                if option['selected']:
                    item['maat'] = option['label']
                    yield item
                else:
                    id = option['artikelNummer']
                    code = option['maatCode']
                    yield Request('https://www.wehkamp.nl/service/product-components/api/pdps/{}?sizeCode={}&CC=C28&SC=8H3&KAC=H27'.format(id, code), self.finalOption, meta={'item':item})
        except:
            yield item

    def finalOption(self, response):
        item = response.meta['item']
        json_data = json.loads(response.body)
        item['price'] = json_data['buyingArea']['pricing']['price']/100
        item['old_price'] = json_data['buyingArea']['pricing']['scratchPrice']/100
        item['rating'] = json_data['buyingArea']['reviewSummary']['rating']
        item['reviews'] = json_data['buyingArea']['reviewSummary']['numberOfReviews']
        properties = json_data['productInformation']['properties']
        for attr in properties:
            if attr['label'] == "vulling":
                item['vulling'] = attr['value']
            if attr['label'] == "vulgewicht (gr/m2)":
                item['vulgewicht (gr/m2)'] = attr['value']
            if attr['label'] == "tijk":
                item['tijk'] = attr['value']

        yield item





# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, json

class dekbedSpider(Spider):
    name = "beddengoed_dekbedovertrek"
    start_urls = ['https://www.beddengoed.com/volwassenen/dekbedovertrek', 'https://www.beddengoed.com/kinderen/dekbedovertrek-kinderen', 'https://www.beddengoed.com/baby-en-peuters/dekbedovertrekken']

    use_selenium = False
    count = 0
    reload(sys)
    sys.setdefaultencoding('utf-8')


    def parse(self, response):
        products = response.xpath('//li[@class="item"]/div[1]/a/@href').extract()
        for i, url in enumerate(products):
            # url = product.xpath('./div/a/@href').extract_first()
            yield Request(url, self.finalParse)
            # break
        next = response.xpath('//a[@class="next ic ic-right"]/@href').extract_first()
        if next:
            url = response.urljoin(next)
            yield Request(url, callback=self.parse)

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
        try:
            item = OrderedDict()
            item['Name'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
            item['Url'] = response.url
            # try:
            #     rating = response.body.split('ratingValue')[-1].split(',')[0].replace('"', '')
            #     item['Rating'] = rating
            # except:
            item['Rating'] = ''

            item['Reviews'] = response.xpath('//a[@id="goto-reviews-form"]/text()').extract_first()
            options = response.xpath('//div[@itemprop="description"]/text()').extract()
            for option in options:
                if 'Merk:' in option:
                    item['Merk'] = option.split(':')[-1].strip()
                elif 'Materiaal:' in option:
                    item['Materiaal'] = option.split(':')[-1].strip()

            oldprices = response.xpath('//span[contains(@id,"old-price")]/text()').re(r'[\d,.]+')
            oldprice = 0.0
            if oldprices:
                oldprice = float(oldprices[0].replace('.', '').replace(',', '.'))

            oldprices = response.xpath('//meta[@itemprop="price"]/@content').re(r'[\d,.]+')
            price = 0.0
            if oldprices:
                price = float(oldprices[0])

            Levering_options = response.xpath('//select[@class="required-entry super-attribute-select"]/option')
            if Levering_options:
                Levering  = {}
                options = json.loads(response.body.split('"options":')[-1].split('}]}},')[0] + '}]')

                for option in options:
                    id= option['products'][0]
                    key = option['label']
                    option_price = option['price']
                    option_oldprice = option['oldPrice']
                    levertijd = response.body.split('var productMap =')[-1].split('var selectedAttributeId')[0].split('"{}":"'.format(id))[-1].split('"')[0]
                    item['maat_option'] = key
                    item['price'] = price + float(option_price)
                    if oldprice:
                        item['old_price'] = oldprice  + float(option_oldprice)
                    else:
                        item['old_price'] = None
                    item['Levertijd'] = levertijd
                    yield item
            else:
                item['maat_option'] = None
                item['price'] = price
                if oldprice:
                    item['old_price'] = oldprice
                else:
                    item['old_price'] = None
                item['Levertijd'] = response.xpath('//div[@class="levertijd"]/text()').extract_first().strip().split(':')[-1].strip()
                yield item
        except Exception as e:
            print e.message


# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, json

class dekbedSpider(Spider):
    name = "slaapvaak_dekbedovertrekken"
    start_urls = ['https://www.slaapvaak.nl/slaapkamer/dekbedovertrekken', 'https://www.slaapvaak.nl/slaapkamer/kinderdekbedovertrekken']

    use_selenium = True
    count = 0
    reload(sys)
    sys.setdefaultencoding('utf-8')


    def parse(self, response):
        products = response.xpath('//div[@class="product-block-inner"]/div[@class="image"]/a/@href').extract()

        for i, url in enumerate(products):

            yield Request(response.urljoin(url), self.parse_option)
            # break
        next = response.xpath('//li[@class="next"]/a/@href').extract_first()
        if next:
            # time.sleep(0.5)
            url = response.urljoin(next)
            yield Request(url, callback=self.parse)

    def parse_option(self, response):
        option_tags = response.xpath('//label[contains(text(), "Maat")]/following-sibling::select/option')
        if option_tags:
            id = response.xpath('//label[contains(text(), "Maat")]/following-sibling::select/@name').extract_first()
            for option_tag in option_tags:
                selected = option_tag.xpath('./@selected').extract_first()
                if selected:
                    item = OrderedDict()
                    # item['Brand'] = response.xpath('//a[@data-role="BRAND"]/text()').extract_first()
                    item['Name'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
                    item['Url'] = response.url

                    oldprices = response.xpath('//span[@class="price-old"]/text()').re(r'[\d,.]+')
                    if oldprices:
                        item['old_price'] = float(''.join(oldprices).replace('.', '').replace(',', '.'))

                    oldprices = response.xpath('//span[@class="price"]/text()').re(r'[\d,.]+')
                    if oldprices:
                        item['price'] = float(''.join(oldprices).replace('.', '').replace(',', '.'))


                    item['maat_option'] = response.xpath('//label[contains(text(), "Maat")]/following-sibling::select/option[@selected="selected"]/text()').extract_first()
                    item['Delivery'] = response.xpath('//div[@class="delivery"]//dd/text()').extract_first()

                    item['attributes'] = '\n'.join(response.xpath('//div[@class="page information active"]/ul/li/text()').extract())

                    yield item
                else:
                    val = option_tag.xpath('./@value').extract_first()
                    str_param = response.xpath('//label[contains(text(), "Maat")]/following-sibling::select/@onchange').extract_first()
                    url = 'https://www.slaapvaak.nl/product/options/' + str_param.split('https://www.slaapvaak.nl/product/options/')[-1].split("';")[0]
                    yield FormRequest(url, self.finalParse, formdata={'bundle_id':'', id:val}, dont_filter=True)
                # time.sleep(0.5)

        else:
            self.finalParse(response)


    def finalParse(self, response):
        # try:
            item = OrderedDict()
            # item['Brand'] = response.xpath('//a[@data-role="BRAND"]/text()').extract_first()
            item['Name'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
            item['Url'] = response.url

            oldprices = response.xpath('//span[@class="price-old"]/text()').re(r'[\d,.]+')
            if oldprices:
                item['old_price'] = float(''.join(oldprices).replace('.', '').replace(',', '.'))

            oldprices = response.xpath('//span[@class="price"]/text()').re(r'[\d,.]+')
            if oldprices:
                item['price'] = float(''.join(oldprices).replace('.', '').replace(',', '.'))


            item['maat_option'] = response.xpath('//label[contains(text(), "Maat")]/following-sibling::select/option[@selected="selected"]/text()').extract_first()
            item['Delivery'] = response.xpath('//div[@class="delivery"]//dd/text()').extract_first()

            item['attributes'] = '\n'.join(response.xpath('//div[@class="page information active"]/ul/li/text()').extract())

            yield item



        # except Exception as e:
        #     print e.message


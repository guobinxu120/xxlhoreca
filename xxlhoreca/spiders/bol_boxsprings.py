# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, json

class dekbedSpider(Spider):
    name = "bol_boxsprings"
    start_urls = ['https://www.bol.com/nl/l/wonen/boxsprings/N/14104/suggestionType/category/suggestedFor/boxspr/originalSearchContext/las_all/originalSection/las/index.html?_requestid=2172493']

    use_selenium = True
    count = 0
    reload(sys)
    sys.setdefaultencoding('utf-8')

    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse, meta={'page':1})
    def parse(self, response):
        products = response.xpath('//li[@itemprop="itemListElement"]/meta[@itemprop="url"]/@content').extract()
        if not products:
            products = response.xpath('//a[@class="product-image product-image--list"]/@href').extract()
            if not products:
                products = response.xpath('//a[@class="hit-area-listpage hit-area__link"]/@href').extract()
                if not products:
                    pass

        for i, url in enumerate(products):

            yield Request(response.urljoin(url), self.parse_option, dont_filter=True)
            # break
        page = response.meta['page']
        if page < 63:
            page = page + 1
            yield Request('https://www.bol.com/nl/l/boxsprings/N/14104/?page={}&view=list'.format(page), self.parse, meta={'page':page})
        # next = response.xpath('//li[contains(@class,"pagination__controls pagination__controls--next")]/a/@href').extract_first()
        # if next:
        #     # time.sleep(0.5)
        #     url = response.urljoin(next)+'&view=list'
        #     yield Request(url, callback=self.parse)
        # else:
        #     pass

    def parse_option(self, response):
        options = response.xpath('//div[@data-test="feature-options"]')
        if options:
            option_tags = options[-1].xpath('./a/@href').extract()
            if option_tags:
                for option_tag in option_tags:
                    # time.sleep(0.5)
                    yield Request(option_tag, self.finalParse, dont_filter=True)
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
            # item['Materiaal'] = attrs[0].strip()
            item['maat_option'] = attrs[0].strip()
            item['Delivery'] = ''.join(response.xpath('//div[@data-test="delivery-info"]/text()').extract()).strip()

            datas = response.xpath('//ul[@class="buy-block__usps check-list--succes check-list--usps"]/li')
            for li_data in datas:
                strdata = ' '.join(li_data.xpath('.//text()').extract())
                # if 'Gratis'  in strdata:
                #     item['Gratis'] = strdata
                if '30 dagen bedenktijd en' in strdata:
                    item['retourneren'] = strdata

            spec_titles = response.xpath('//dl[@class="specs__list"]/dt[@class="specs__title"]/text()').extract()
            spec_vals_tag = response.xpath('//dl[@class="specs__list"]/dd[@class="specs__value"]')
            spec_vals = []
            for tag in spec_vals_tag:
                txt_att = ''.join(tag.xpath('.//text()').extract())
                spec_vals.append(txt_att)
            item['maat_option'] = None
            for i, title in enumerate(spec_titles):
                # if 'Materiaal tijk' in title:
                #     item['Materiaal tijk'] = spec_vals[i].strip()
                # elif 'Materiaal vulling' in title:
                #     item['Materiaal vulling'] = spec_vals[i].strip()
                # elif 'Anti-allergie' in title:
                #     item['Anti-allergie'] = spec_vals[i].strip()
                # elif 'Warmteklasse' in title:
                #     item['Warmteklasse'] = spec_vals[i].strip()

                if 'Afmetingen bxl' in title:
                    item['maat_option'] = spec_vals[-1].strip()
            if not item['maat_option'] or not 'x' in item['maat_option']:
                item['maat_option'] = response.xpath('//div[@data-test="feature-options"]/a[contains(@class, "is-active")]/span/text()').extract_first()
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

            # attrs = response.xpath('//ul[@class="product-small-specs product-small-specs--large"]/li/text()').extract()
            # item['Materiaal'] = attrs[0].strip()
            # item['maat_option'] = attrs[0].strip()
            item['Delivery'] = ''.join(response.xpath('//div[@data-test="delivery-info"]/text()').extract()).strip()

            datas = response.xpath('//ul[@class="buy-block__usps check-list--succes check-list--usps"]/li')
            for li_data in datas:
                strdata = ' '.join(li_data.xpath('.//text()').extract())
                # if 'Gratis'  in strdata:
                #     item['Gratis'] = strdata
                if '30 dagen bedenktijd en' in strdata:
                    item['retourneren'] = strdata

            spec_titles = response.xpath('//dl[@class="specs__list"]/dt[@class="specs__title"]/text()').extract()
            spec_vals_tag = response.xpath('//dl[@class="specs__list"]/dd[@class="specs__value"]')
            spec_vals = []
            for tag in spec_vals_tag:
                txt_att = ''.join(tag.xpath('.//text()').extract())
                spec_vals.append(txt_att)
            item['maat_option'] = None
            for i, title in enumerate(spec_titles):
                # if 'Materiaal tijk' in title:
                #     item['Materiaal tijk'] = spec_vals[i].strip()
                # elif 'Materiaal vulling' in title:
                #     item['Materiaal vulling'] = spec_vals[i].strip()
                # elif 'Anti-allergie' in title:
                #     item['Anti-allergie'] = spec_vals[i].strip()
                # elif 'Warmteklasse' in title:
                #     item['Warmteklasse'] = spec_vals[i].strip()

                if 'Afmetingen bxl' in title:
                    item['maat_option'] = spec_vals[-1].strip()
            if not item['maat_option'] or not 'x' in item['maat_option']:
                item['maat_option'] = response.xpath('//div[@data-test="feature-options"]/a[contains(@class, "is-active")]/span/text()').extract_first()
            yield item

        except Exception as e:
            print e.message


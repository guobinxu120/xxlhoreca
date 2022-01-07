# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, json

class dekbedSpider(Spider):
    name = "leenbakker_dekbedovertrek"
    start_urls = ['https://www.leenbakker.nl/bed-en-toebehoren/beddengoed/dekbedovertrekken']

    use_selenium = True
    count = 0
    reload(sys)
    models = {}
    sys.setdefaultencoding('utf-8')
    headers = ['name', 'url', 'price', 'reviews', 'delivery']
    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse, meta={'page':1})
    def parse(self, response):
        products = response.xpath('//div[contains(@id,"CatalogEntryProdImg")]//a[contains(@id,"catalogEntry_img")]/@href').extract()

        for i, url in enumerate(products):
            yield Request(response.urljoin(url), self.finalParse, dont_filter=True)

        nexts = response.xpath('//a[contains(@id,"WC_SearchBasedNavigationResults_pagination_link_right_")]/@href').extract_first()

        if nexts:
            # url = nexts[-1].xpath('./a/@href').extract_first()
            yield Request(nexts, callback=self.parse)

    # def parse_option(self, response):
    #     options = response.xpath('//select[@class="select roundless skin-gray"]')
    #     if options:
    #         url = options[0].xpath('./option/@data-link').extract_first()
    #         yield Request(response.urljoin(url), self.finalParse, dont_filter=True)


    def finalParse(self, response):
        try:
            item = OrderedDict()
            for key in self.headers:
                item[key] = None
            # item['brand'] = response.xpath('//div[@class="page-header__part page-header__brand"]/a/text()').extract_first()
            item['name'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
            item['url'] = response.url
            # attr_data = json.loads(response.body.split('application/ld+json">')[-1].split('</script>')[0].strip())
            # try:
            #     rating = attr_data['aggregateRating']['ratingValue']
            # item['reviews'] = response.xpath('//button[@class="bv_numReviews_text"]/text()').re(r'[\d]+')[0]
            item['reviews'] =0
            # except:
            #     pass

            price_tag = response.xpath('//div[@class="name_partnumber_price"]')
            oldprices = price_tag[1].xpath('.//span[@itemprop="price"]//text()').re(r'[\d,.]+')
            # oldprice = 0.0
            if oldprices:
                oldprice = '.'.join(oldprices).replace(' ', '')
            item['price'] = oldprice
            item['delivery'] = '\n'.join(response.xpath('//div[@class="prod_description_usps"]/ul/li/a/text()').extract())


            options = response.xpath('//select[@name="sizeVariantPicker"]/option')
            next_url = None
            flag = False
            for i, select in enumerate(options):
                option_url = select.xpath('./@value').extract_first()
                txt_option = select.xpath('./text()').extract_first()
                if not option_url:
                    item['maat'] = txt_option
                    flag = True
                if flag and option_url:
                    next_url = option_url
                    break


            trs = response.xpath('//ul[@class="specification_PDP"]')
            lis = trs[0].xpath('./li')
            for tr in lis:
                key = ''.join(tr.xpath('./span[1]//text()').extract()).strip()
                val = ''.join(tr.xpath('./span[2]//text()').extract()).strip()

                if 'Materiaal:' == key:
                    item['Materiaal'] = val
                    if not key in self.headers:
                        self.headers.append(key)
                # elif 'Garantie'  in key:
                #     item[key] = val
                #     if not key in self.headers:
                #         self.headers.append(key)
                # elif 'Instopstrook' in key:
                #     item[key] = val
                #     if not key in self.headers:
                #         self.headers.append(key)
                # elif 'Materiaal type' == key:
                #     item[key] = val
                #     if not key in self.headers:
                #         self.headers.append(key)
                # elif 'Materiaal' == key:
                #     item[key] = val
                #     if not key in self.headers:
                #         self.headers.append(key)

            yield item
            self.count += 1
            print(self.count)
            self.models[item['url']] = item

            if next_url:
                yield Request(response.urljoin(next_url), self.finalParse, dont_filter=True)

        except Exception as e:
            print(e.message)

            # yield item






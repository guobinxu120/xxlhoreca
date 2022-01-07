# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
from scrapy.http import TextResponse
import sys
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time, json, requests

class dekbedSpider(Spider):
    name = "boxspring"
    start_urls = ['https://www.dekbed-discounter.nl/boxspring/boxspring-kopen/']

    use_selenium = False
    count = 0
    reload(sys)
    sys.setdefaultencoding('utf-8')
    models = []
    headers = []
    def parse(self, response):
        products = response.xpath('//div[@id="products-container"]/div[@class="row"]/div[contains(@class,"product-block")]')
        for i, product in enumerate(products):
            url = product.xpath('./div/a/@href').extract_first()
            yield Request(url, self.parse_option)
            # break
        next = response.xpath('//a[@class="next"]/@href').extract_first()
        if next:
            url = response.urljoin(next)
            yield Request(url, callback=self.parse)

    def parse_option(self, response):
        option_tags = response.xpath('//div[@class="product-configure-options-option"]/select')
        id_pro = response.xpath('//div[@class="yotpo bottomLine"]/@data-product-id').extract_first()

        if option_tags:
            options = {}
            url = 'https://www.dekbed-discounter.nl/product/options/{}/'.format(id_pro)
            for i, option_select in enumerate(option_tags):
                # if i == 0:
                options1= option_tags[i].xpath('./option')
                name1= option_tags[i].xpath('./@name').extract_first()
                key1= option_tags[i].xpath('./parent::div/label/text()').extract_first().replace(':', '').strip()
                options[key1] = {'name': name1, 'options': {}}
                for option_tag in options1:
                    option = {}
                    id = option_tag.xpath('./@value').extract_first()
                    variant = option_tag.xpath('./text()').extract_first()
                    disabled = option_tag.xpath('./@disabled')
                    if not disabled:
                        # option[id] = variant
                        options[key1]['options'][id] = variant
            formdata = {}
            formdata['bundle_id'] = ''
            option_json = {}
            for i, key1 in enumerate(options.keys()):
                if i > 0: continue
                for option_p1 in options[key1]['options'].keys():
                    formdata[options[key1]['name']] = option_p1
                    option_json[key1] = options[key1]['options'][option_p1]
                    if len(options.keys() ) == 1:
                        yield Request(response.url + '?id={}'.format(id_pro), callback=self.finalParse, meta={'options': option_json}, dont_filter=True)

                    for ii, key2 in enumerate(options.keys()):
                        if ii != i+1 : continue
                        for option_p2 in options[key2]['options'].keys():
                            formdata[options[key2]['name']] = option_p2
                            option_json[key2] = options[key2]['options'][option_p2]
                            if ii+1 == len(options.keys()):
                                yield FormRequest(url, self.finalParse, formdata=formdata, meta={'options': option_json}, dont_filter=True)
                            elif ii+1 < len(options.keys()):
                                for iii, key3 in enumerate(options.keys()):
                                    if iii != ii+1 : continue
                                    for option_p3 in options[key3]['options'].keys():
                                        formdata[options[key3]['name']] = option_p3
                                        option_json[key3] = options[key3]['options'][option_p3]
                                        if iii+1 == len(options.keys()):
                                            yield FormRequest(url, self.finalParse, formdata=formdata, meta={'options': option_json}, dont_filter=True)
                                        elif iii+1 < len(options.keys()):
                                            for iiii, key4 in enumerate(options.keys()):
                                                if iiii != iii+1 : continue
                                                for option_p4 in options[key4]['options'].keys():
                                                    formdata[options[key4]['name']] = option_p4
                                                    option_json[key4] = options[key4]['options'][option_p4]
                                                    if iiii+1 == len(options.keys()):
                                                        yield FormRequest(url, self.finalParse, formdata=formdata, meta={'options': option_json}, dont_filter=True)
                                                    elif iiii+1 < len(options.keys()):
                                                        for iiiii, key5 in enumerate(options.keys()):
                                                            if iiiii != iiii+1 : continue
                                                            for option_p5 in options[key5]['options'].keys():
                                                                formdata[options[key5]['name']] = option_p5
                                                                option_json[key5] = options[key5]['options'][option_p5]
                                                                if iiii+1 == len(options.keys()):
                                                                    yield FormRequest(url, self.finalParse, formdata=formdata, meta={'options': option_json}, dont_filter=True)

        else:
            item = OrderedDict()
            item['Name'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
            item['Url'] = response.url
            item['Reviews'] = response.xpath('//div[@class="yotpo-bottomline pull-left  star-clickable"]/a/text()').extract_first()

            item['Merk'] = response.xpath('//span[@itemprop="brand"]/text()').extract_first()
            item['Levertijd'] = ''.join(response.xpath('//span[@class="on-stock"]/text()').extract()).strip()
            # item['Maat'] = response.meta['maat'].strip()
            # item['montagekeuze'] = response.meta['montagekeuze'].strip()
            item['Price'] = response.xpath('//span[@itemprop="price"]/text()').extract_first()
            if item['Price']:
                item['Price'] = item['Price'].replace('.', '').replace(',', '.')
            int_old = ''.join(response.xpath('//span[@class="price-old"]/text()').extract()).replace('.', '').replace(',', '')
            decimal_old= ''.join(response.xpath('//span[@class="price-old"]/span[@class="productpriceDecimal"]/text()').extract())
            if decimal_old !='':
                item['Price_Old'] = int_old +'.' +decimal_old
            else:
                item['Price_Old'] = int_old

            specs = response.xpath('//div[@id="product-text"]/table')
            if specs:
                for tr in specs[-1].xpath('.//tr'):
                    key = ''.join(tr.xpath('./td[1]//text()').extract()).strip()
                    val = '\n'.join(tr.xpath('./td[2]//text()').extract()).strip().replace('&nbsp;', ' ')
                    item[key] = val

            print(self.count)
            self.count += 1
            url = 'https://staticw2.yotpo.com/batch'
            id = response.xpath('//div[@class="yotpo bottomLine"]/@data-product-id').extract_first()
            app_key = response.body.split('src="//staticw2.yotpo.com/')[-1].split('/')[0]
            method = '%5B%7B%22method%22%3A%22main_widget%22%2C%22params%22%3A%7B%22pid%22%3A%22{}%22%7D%7D%2C%7B%22method%22%3A%22bottomline%22%2C%22params%22%3A%7B%22pid%22%3A%22{}%22%2C%22link%22%3Anull%2C%22skip_average_score%22%3Afalse%2C%22main_widget_pid%22%3A%22{}%22%7D%7D%5D'.format(id, id, id)
            formdata = {
                'methods': method,
                'app_key': app_key,
                'is_mobile': 'false',
                'widget_version': '2018-07-11_08-23-59'
            }
            headers= {
                'Accept': 'application/json'
            }
            ddd = [{"method":"main_widget","params":{"pid":id}},{"method":"bottomline","params":{"pid":id,"link":'null',"skip_average_score":'false',"main_widget_pid":id}}]
            formdata['methods'] = json.dumps(ddd)
            fields = item.keys()
            for field in fields:
                if not field in self.headers:
                    self.headers.append(field)
            yield FormRequest(url, self.getReview, formdata=formdata, meta={'item':item}, headers=headers, dont_filter=True)
                    # options2= option_tags[1].xpath('./option')
                    # name2= option_tags[1].xpath('./@name').extract_first()
                    # for option2 in options2:
                    #     id1 = option2.xpath('./@value').extract_first()
                    #     variant1 = option2.xpath('./text()').extract_first()
                    #     disabled1 = option2.xpath('./@disabled')
                    #     if not disabled1:
                    #
                    #         formdata = {
                    #             str(name1): str(id),
                    #             str(name2): str(id1),
                    #             'bundle_id':''
                    #         }
                    #         yield FormRequest(url, self.finalParse, formdata=formdata, meta={'maat': variant, 'montagekeuze': variant1}, dont_filter=True)



    def finalParse(self, response):
        item = OrderedDict()
        item['Name'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
        item['Url'] = response.url
        # try:
        #     rating = response.body.split('ratingValue')[-1].split(',')[0].replace('"', '')
        #     item['Rating'] = rating
        # except:
        #     item['Rating'] = ''

        item['Reviews'] = response.xpath('//div[@class="yotpo-bottomline pull-left  star-clickable"]/a/text()').extract_first()

        item['Merk'] = response.xpath('//span[@itemprop="brand"]/text()').extract_first()
        item['Levertijd'] = ''.join(response.xpath('//span[@class="on-stock"]/text()').extract()).strip()
        # item['Maat'] = response.meta['maat'].strip()
        # item['montagekeuze'] = response.meta['montagekeuze'].strip()
        for key in response.meta['options'].keys():
            item[key] = response.meta['options'][key]

        item['Price'] = response.xpath('//span[@itemprop="price"]/text()').extract_first()
        if item['Price']:
            item['Price'] = item['Price'].replace('.', '').replace(',', '.')
        int_old = ''.join(response.xpath('//span[@class="price-old"]/text()').extract()).replace('.', '').replace(',', '')
        decimal_old= ''.join(response.xpath('//span[@class="price-old"]/span[@class="productpriceDecimal"]/text()').extract())
        if decimal_old !='':
            item['Price_Old'] = int_old +'.' +decimal_old
        else:
            item['Price_Old'] = int_old

        specs = response.xpath('//div[@id="product-text"]/table')
        if specs:
            for tr in specs[-1].xpath('.//tr'):
                key = ''.join(tr.xpath('./td[1]//text()').extract()).strip()
                val = '\n'.join(tr.xpath('./td[2]//text()').extract()).strip().replace('&nbsp;', ' ')
                item[key] = val

        print(self.count)
        self.count += 1
        url = 'https://staticw2.yotpo.com/batch'
        id = response.xpath('//div[@class="yotpo bottomLine"]/@data-product-id').extract_first()
        app_key = response.body.split('src="//staticw2.yotpo.com/')[-1].split('/')[0]
        method = '%5B%7B%22method%22%3A%22main_widget%22%2C%22params%22%3A%7B%22pid%22%3A%22{}%22%7D%7D%2C%7B%22method%22%3A%22bottomline%22%2C%22params%22%3A%7B%22pid%22%3A%22{}%22%2C%22link%22%3Anull%2C%22skip_average_score%22%3Afalse%2C%22main_widget_pid%22%3A%22{}%22%7D%7D%5D'.format(id, id, id)
        formdata = {
            'methods': method,
            'app_key': app_key,
            'is_mobile': 'false',
            'widget_version': '2018-07-11_08-23-59'
        }
        headers= {
            'Accept': 'application/json'
        }
        ddd = [{"method":"main_widget","params":{"pid":id}},{"method":"bottomline","params":{"pid":id,"link":'null',"skip_average_score":'false',"main_widget_pid":id}}]
        formdata['methods'] = json.dumps(ddd)
        fields = item.keys()
        for field in fields:
            if not field in self.headers:
                self.headers.append(field)
        yield FormRequest(url, self.getReview, formdata=formdata, meta={'item':item}, headers=headers, dont_filter=True)

    def getReview(self, response):
        item = response.meta['item']
        try:
            jsondata = json.loads(response.body)
            Reviews = jsondata[0]['result'].split('Beoordelingen')[0].split('>')[-1]
            item['Reviews'] = Reviews
            self.models.append(item)
            yield item
        except:
            self.models.append(item)
            yield item



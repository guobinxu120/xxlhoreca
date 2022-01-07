# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json, csv
from scrapy import signals

class XxlhorecaPipeline(object):
    def __init__(self):
            #Instantiate API Connection
            self.files = {}
            print ">>>>>> Initialize pipeline."

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline


    def spider_opened(self, spider):
        pass
        #open a static/dynamic file to read and write to
        # path = spider.path
        #
        # file = open(path+'%s.json' % spider.hotel_info[4], 'w+b')
        # self.files[spider] = file
        # #file.write('{"HotelName":"{}","Rates":['.format("My hotel"))
        # # header = '{"HotelName":"%s",\
        # # 			"HotelInfo":{ \
        # # 				"cityOrininId":"%s" \
        # # 				"cityOriginName":"%s" \
        # # 				"propertyId":"%s"\
        # # 			},\
        # # 		"Rates":[' %
        # # 		(spider.hotel_info[0], spider.hotel_info[1], spider.hotel_info[4], spider.hotel_info[9])
        #
        # header = '{"HotelName":"%s","HotelInfo":{"cityOriginId":"%s","cityOriginName":"%s","propertyId":"%s"},"Rates":[ \n' % \
        #      (spider.hotel_info[9], spider.hotel_info[0], spider.hotel_info[1], spider.hotel_info[4])
        #
        # file.write(header)
        #
        # log_path = '/'.join(path.split('/')[:-2]) + "/log.csv"
        # print "Log Path:", log_path
        # if not os.path.exists(log_path):
        #     log_file = open(log_path, "a")
        #     header = "cityOriginId,cityOriginName,propertyOriginName,hotel_desc,propertyAddress,Phone,PostalCode,propertyLatitude,propertyLongitude,vendorName1,propertyId1,propertyURL1,queryDate1,allProperties1,destinationType1,propertyClass1,reviewScore1,page1,position1,numberOfReviews1,vendorName2,propertyId2,propertyURL2,queryDate2,allProperties2,destinationType2,propertyClass2,reviewScore2,page2,position2,numberOfReviews2\n"
        #     log_file.writelines([header])
        #     log_file.close()
        #
        #
        # self.exporter = JsonLinesItemExporter(file)
        # self.exporter.start_exporting()

    def spider_closed(self, spider):
        # pass
        if spider.name == 'boxspring':
            headers = spider.headers
            ff = open("boxspring.csv","wb")
            filewriter1 = csv.writer(ff, delimiter=',',quoting=csv.QUOTE_ALL)
            filewriter1.writerow(headers)
            flag = False
            for item in spider.models:
                row = []
                for key in headers:
                    if key in item.keys():
                        row.append(item[key])
                    else:
                        row.append('')

                filewriter1.writerow(row)
            ff.close()

        elif spider.name == 'fonq_dekbed' or spider.name =='google_shopping' or spider.name == "find" or spider.name == "architonic":
            param = spider.models
            headers = spider.headers
            ff = open("fonq_dekbed1.csv","wb")
            filewriter1 = csv.writer(ff, delimiter=',',quoting=csv.QUOTE_ALL)

            filewriter1.writerow(headers)
            for row in param.keys():
                item = param[row]
                row_item = []
                for key in headers:
                    if key in item.keys():
                        row_item.append(item[key])
                    else:
                        row_item.append('')
                filewriter1.writerow(row_item)
            ff.close()

        elif spider.name =='fonq_boxspring':
            param = spider.models
            headers = spider.headers
            ff = open("fonq_boxspring1.csv","wb")
            filewriter1 = csv.writer(ff, delimiter=',',quoting=csv.QUOTE_ALL)

            filewriter1.writerow(headers)
            for row in param:
                item = row
                row_item = []
                for key in headers:
                    if key in item.keys():
                        row_item.append(item[key])
                    else:
                        row_item.append('')
                filewriter1.writerow(row_item)
            ff.close()

        elif spider.name =='fonq_dekbedovertrek':
            param = spider.models
            headers = spider.headers
            ff = open("fonq_dekbedovertrek1.csv","wb")
            filewriter1 = csv.writer(ff, delimiter=',',quoting=csv.QUOTE_ALL)

            filewriter1.writerow(headers)
            for row in param.keys():
                item = param[row]
                row_item = []
                for key in headers:
                    if key in item.keys():
                        row_item.append(item[key])
                    else:
                        row_item.append('')
                filewriter1.writerow(row_item)
            ff.close()

    def process_item(self, item, spider):
        # self.exporter.export_item(dict(item))
        # file = self.files[spider]
        # file.write(",")
        return item

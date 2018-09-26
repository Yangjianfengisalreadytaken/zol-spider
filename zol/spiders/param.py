# -*- coding: UTF-8 -*-

import pymysql
import sys

from pip._vendor.requests.packages import chardet
from scrapy import Spider, Request, Item, Selector
from scrapy.spiders import CrawlSpider

from zol import settings
from zol.items import MobileItem, BaseMsg, ParamsScreen, ParamsHardware, ParamsNetwork, ParamsCamera, ParamsAppear, \
    AdditionalFunc, Guarantee

reload(sys)
sys.setdefaultencoding('utf8')


def get_params_name():
    names = {}
    # base_msg
    names["上市日期"] = "market_date"
    names["参考报价"] = "price"
    names["手机类型"] = "type"
    names["操作系统"] = "system"
    names["手机附件"] = "attachment"
    # screen
    names["触摸屏类型"] = "type"
    names["主屏尺寸"] = "size"
    names["主屏材质"] = "texture"
    names["主屏分辨率"] = "resolution"
    names["屏幕像素密度"] = "ppi"
    names["窄边框"] = "border"
    names["屏幕技术"] = "technology"
    names["屏幕占比"] = "ratio"
    names["其他屏幕参数"] = "others"
    names["副屏参数"] = "vice_screen"
    # hardware
    names["CPU型号"] = "cpu_type"
    names["CPU频率"] = "cpu_fre"
    names["核心数"] = "core_num"
    names["GPU型号"] = "gpu_type"
    names["RAM容量"] = "ram"
    names["ROM容量"] = "rom"
    names["存储卡"] = "storage_card"
    names["扩展容量"] = "extand_storage"
    names["电池类型"] = "battery_type"
    names["电池容量"] = "battery_size"
    names["续航时间"] = "employ_duration"
    names["充电时间"] = "charge_duration"
    names["其他硬件参数"] = "others"
    names["理论通话时间"] = "phone_duration"
    names["理论待机时间"] = "await_duration"
    # network
    names["4G网络"] = "network_4g"
    names["3G网络"] = "network_3g"
    names["支持频段"] = "frequency"
    names["SIM卡类型"] = "sim_type"
    names["WLAN功能"] = "wlan"
    names["导航"] = "director"
    names["连接与共享"] = "connect"
    names["机身接口"] = "connector"
    names["其他网络参数"] = "others"
    # camera
    names["摄像头总数"] = "count"
    names["后置摄像头"] = "background"
    names["前置摄像头"] = "foreground"
    names["传感器类型"] = "sensor_type"
    names["闪光灯"] = "flashlight"
    names["视频拍摄"] = "video"
    names["光圈"] = "aperture"
    names["摄像头特色"] = "feature"
    names["拍照功能"] = "photo"
    names["摄像头类型"] = "type"
    names["其他摄像头参数"] = "others"
    names["传感器型号"] = "model"
    # appear
    names["造型设计"] = "model"
    names["机身颜色"] = "color"
    names["手机尺寸"] = "size"
    names["手机重量"] = "weight"
    names["机身材质"] = "texture"
    names["操作类型"] = "operate"
    names["指纹识别设计"] = "fingerprint"
    names["机身特点"] = "character"
    names["机身接口"] = "connector"
    names["其他外观参数"] = "others"
    # additional_func
    names["感应器类型"] = "inductor_type"
    names["音频支持"] = "audio"
    names["视频支持"] = "video"
    names["图片支持"] = "picture"
    names["多媒体技术"] = "media"
    names["常用功能"] = "common_func"
    names["商务功能"] = "business_func"
    names["服务特色"] = "service"
    names["三防功能"] = "proofings"
    names["其他功能参数"] = "others"
    # guarantee
    names["保修政策"] = "policy"
    names["质保时间"] = "duration"
    names["质保备注"] = "note"
    names["客服电话"] = "phone"
    names["电话备注"] = "phone_note"
    names["详细内容"] = "details"
    return names

# def get_table_name():
#     tables = {}
#     tables["屏幕"] = ParamsScreen()
#     tables["硬件"] = ParamsHardware()
#     tables["网络与连接"] = ParamsNetwork()
#     tables["摄像头"] = ParamsCamera()
#     tables["外观"] = ParamsAppear()
#     tables["更多功能与服务"] = AdditionalFunc()
#     tables["保修信息"] = Guarantee()

class MobileDetailSpider(Spider):
    name = "params"
    allowed_domains = ["zol.com.cn"]
    params = get_params_name()

    def __init__(self):
        pass

    def start_requests(self):
        yield Request(url="http://mobile.zol.com.cn/manu_list.html", callback=self.parse_brand_list)
    # yield Request(url="http://detail.zol.com.cn/cell_phone/index1184692.shtml", callback=self.parse_mobile)

    def parse_brand_list(self, response):
        # file = open("aaa.html", "wb");
        # file.write(response.body)
        brands = response.xpath("//ul[@class='brandsTxt clearfix']/li")
        for brand in brands:
            url =response.urljoin(brand.xpath("./a/@href").extract_first())
            yield Request(url=url, callback=self.parse_brand)

    def parse_brand(self, response):
        mobiles = response.xpath("//ul[@class='timeline-products clearfix']/li")
        for mobile in mobiles:
            url = mobile.xpath("./a/@href").extract_first();
            yield Request(url=url, callback=self.parse_mobile)

    def parse_mobile(self, response):
        params = response.xpath("//a[@class='_j_MP_more more']/@href").extract_first()
        url = response.urljoin(params)
        price = str(response.xpath("//b[@class='price-sign']/text()").extract_first() or "") \
                + response.xpath("//b[@class='price-type']/text()").extract_first()
        yield Request(url=url, callback=self.parse_params, meta={"price":price})
        pass

    def parse_params(self, response):
        tables = response.xpath("//div[@id='newTb']/table")
        params_table = {}
        for table in tables:
            type = table.xpath(".//th/text()").extract_first().encode("utf-8")
            # print "type:" + type
            params_table[type] = table

        item = MobileItem()
        # 解析基本参数与手机附件
        attach = params_table.get("手机附件")
        base_msg = params_table.get("基本参数")
        item["base_msg"] = self.parse_base_msg(response, attach, base_msg)
        # 解析屏幕参数
        item["params_screen"] = self.parse_tables("屏幕", params_table, ParamsScreen())
        # 解析硬件参数
        item["params_hardware"] = self.parse_tables("硬件", params_table, ParamsHardware())
        # 解析网络与连接参数
        item["params_network"] = self.parse_tables("网络与连接", params_table, ParamsNetwork())
        # 解析摄像头参数
        item["params_camera"] = self.parse_tables("摄像头", params_table, ParamsCamera())
        # 解析外观参数
        item["params_appear"] = self.parse_tables("外观", params_table, ParamsAppear())
        # 解析更多功能与服务参数
        item["addition_func"] = self.parse_tables("更多功能与服务", params_table, AdditionalFunc())
        # 解析保修信息参数
        item["guarantee"] = self.parse_tables("保修信息", params_table, Guarantee())

        yield item

    # 解析手机基本参数与手机附件
    def parse_base_msg(self, response, p_attachment, base_msg):
        item = BaseMsg()
        item["price"] = response.meta['price']
        directors = response.xpath("//div[@class='breadcrumb']/a[@href]")
        item["url"] = response.url
        item["brand"] = directors[2].xpath("./text()").extract_first()
        item["name"] = directors[3].xpath("./text()").extract_first()
        # tables = response.xpath("//div[@class='newTb']/table")
        # print response.body
        if base_msg is not None:
            params = base_msg.xpath(".//li")
            for param in params:
                p_name = param.xpath("./span/text()")[0].extract()
                p_value = ""
                texts = param.xpath("./span/a/text()")
                if texts is None or len(texts)==0:
                    p_value = param.xpath("./span/text()")[1].extract()
                else:
                    for text in texts:
                        p_value = p_value + text.extract() + "\n"

                # print p_name.decode("utf-8").encode('gb2312')
                # fencoding = chardet.detect(p_name.encode("utf-8"))
                # print fencoding
                if not self.params.has_key(p_name.encode("utf-8")):
                    continue
                type = self.params[p_name.encode("utf-8")]
                item[type] = p_value

        # 解析手机附件
        if p_attachment is None:
            return item
        attachment = ""
        attachments = p_attachment.xpath(".//span")[1].xpath(".//text()").extract()
        for a in attachments:
            attachment = attachment + a + "\n"
        item["attachment"] = attachment
        return item

    # 解析参数表
    def parse_tables(self, type, params_table, item):
        table = params_table.get(type)
        if table is None:
            return item
        params = table.xpath(".//li")
        for param in params:
            p_name = param.xpath("./span/text()")[0].extract()
            p_value = ""
            texts = param.xpath("./span/a/text()")
            if texts is None or len(texts) is 0:
                p_value = param.xpath("./span/text()")[1].extract()
            else:
                for text in texts:
                    p_value = p_value + text.extract() + "\n"
            # print "p_name:"+p_name
            if not self.params.has_key(p_name.encode("utf-8")):
                continue
            type = self.params[p_name.encode("utf-8")]
            item[type] = p_value
        return item

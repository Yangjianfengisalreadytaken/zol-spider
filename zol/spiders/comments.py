# -*- coding: UTF-8 -*-
import json

import pymysql
from scrapy import Spider, Request, Selector
from scrapy.spiders import CrawlSpider

from zol import settings
from zol.items import MobileItem, Evaluate, EvaluateItem


class MobileCommentsSpider(Spider):
    page_size = 10
    name = "comments"
    allowed_domains = ["zol.com.cn"]
    num = 0

    def __init__(self):
        pass

    def start_requests(self):
        yield Request(url="http://mobile.zol.com.cn/manu_list.html", callback=self.parse_brand_list)
        # yield Request(url="http://detail.zol.com.cn/cell_phone/index1184692.shtml", callback=self.parse_mobile)

    # 解析品牌目录
    def parse_brand_list(self, response):
        # file = open("aaa.html", "wb");
        # file.write(response.body)
        brands = response.xpath("//ul[@class='brandsTxt clearfix']/li")
        for brand in brands:
            url =response.urljoin(brand.xpath("./a/@href").extract_first())
            yield Request(url=url, callback=self.parse_brand)

    # 解析品牌所有款式手机
    def parse_brand(self, response):
        mobiles = response.xpath("//ul[@class='timeline-products clearfix']/li")
        for mobile in mobiles:
            url = mobile.xpath("./a/@href").extract_first();
            yield Request(url=url, callback=self.parse_mobile)

    # 解析某款手机主页面（跳转到评测页面）
    def parse_mobile(self, response):
        # print "url:"+response.url
        comments = response.xpath("//li[@class='nav__item--comment']/a/@href").extract_first()
        url = response.urljoin(comments)
        yield Request(url=url, callback=self.parse_comments)

    # 解析手机评测页面
    def parse_comments(self, response):
        # print "url:"+response.url
        name = response.xpath("//div[@class='breadcrumb']/a[last()]/text()").extract_first()
        # 解析头部综合评分
        yield self.parse_score(response, name)

        # 解析每个人的评论
        comments_item = response.xpath("//div[@class='comments-item']")
        for comment_item in comments_item:
            yield self.parse_comment_item(comment_item, name)

        # 生成查看更多的ajax_url并跟进链接解析
        comment_nums = int(response.xpath("//div[@class='total-num total-num-tip']/span/text()").extract_first()[:-3])
        pro_id = int(response.url.split("/")[-2])
        page_nums = (comment_nums + self.page_size - 1) / self.page_size
        for num in range(3, page_nums):
            ajax_url = "http://detail.zol.com.cn/xhr4_Review_GetList_%5EproId="
            ajax_url += str(pro_id) + "%5Epage=";
            ajax_url += str(num) + ".html";
            # print ajax_url
            yield Request(url=ajax_url, callback=self.parse_ajax_items, meta={"name":name})
        # "http://detail.zol.com.cn/xhr4_Review_GetList_%5EproId=1184692%5Epage=3.html"
        pass

    # 解析手机总体得分
    def parse_score(self, response, name):
        # print "url:"+response.url
        item = MobileItem()
        item["name"] = name
        evaluate = Evaluate()
        # 解析评分
        scores = response.xpath("//div[@class='review-comments-score clearfix']")
        evaluate["total"] = scores.xpath("./div[@class='total-score']/strong/text()").extract_first()
        grades = scores.xpath("./div[@class='features-score features-score-5']/div[@class='features-circle']")
        for grade in grades:
            type = grade.xpath("./div[@class='circle-text']/text()").extract_first().encode("utf-8")
            value = grade.xpath("./div[@class='circle-value']/text()").extract_first()
            if type == "性价比":
                evaluate["cost"] = value
            elif type == "性能":
                evaluate["property"] = value
            elif type == "续航":
                evaluate["endurance"] = value
            elif type == "外观":
                evaluate["appearance"] = value
            elif type == "拍照":
                evaluate["photograph"] = value
        # 解析大家都说（优点和缺点）
        comment_words = response.xpath("//div[@class='comments-words comments-words-more']")
        advantage = ""
        disadvantage = ""
        goods = comment_words.xpath("./ul/li[@class='good-words']/a")
        for good in goods:
            words = good.xpath(".//text()").extract()
            for word in words:
                advantage = advantage + word
            advantage = advantage + ","
        bads = comment_words.xpath("./ul/li[@class='bad-words']/a")
        for bad in bads:
            words = bad.xpath(".//text()").extract()
            for word in words:
                disadvantage = disadvantage + word
            disadvantage = disadvantage + ","
        evaluate["advantage"] = advantage
        evaluate["disadvantage"] = disadvantage
        # 保存总体评分
        item["evaluate"] = evaluate

        return item

    # 解析一条点评
    def parse_comment_item(self, selector, name):
        # 页面未显示全部内容
        view_more = selector.xpath(".//div[@class='view-more']")
        if view_more is not None and len(view_more) is not 0:
            tag = selector.xpath(".//div[@class='tag']/text()").extract_first()
            url = view_more[0].xpath("./a/@href").extract_first()
            # print "tag:"+tag+" url:"+url
            return Request(url=url, callback=self.parse_comment_detail, meta={"tag":tag, "mobileName":name})

        # 从页面提取全部内容
        item = MobileItem()
        item["name"] = name
        evaluate_item = EvaluateItem()
        # 解析用户基本信息
        user = selector.xpath("./div[@class='comments-user']")
        evaluate_item["name"] = user.xpath("./a[@class='name']/text()").extract_first()
        evaluate_item["position"] = user.xpath("./div[@class='tag']/text()").extract_first()
        shop_msgs = user.xpath("./p/text()").extract()
        for shop_msg in shop_msgs:
            if len(shop_msg.split("：")) is not 2:
                continue
            type = shop_msg.split("：")[0].encode("utf-8")
            value = shop_msg.split("：")[1]
            if type == "价格":
                evaluate_item["price"] = value
            elif type == "时间":
                evaluate_item["date"] = value
            elif type == "地点":
                evaluate_item["place"] = value
        # 解析评论内容
        content = selector.xpath("./div[@class='comment-list-content']")[0]
        evaluate_item["title"] = content.xpath("./div[@class='title']/a/text()").extract_first()
        evaluate_item["content"] = content.xpath(".//div[@class='words-article']/p/text()").extract_first()
        words = content.xpath(".//div[@class='words']")
        for word in words:
            type = word.xpath("./strong/@class").extract_first()
            value = word.xpath("./p/text()").extract_first()
            if type == "good":
                evaluate_item["advantage"] = value
            elif type == "bad":
                evaluate_item["disadvantage"] = value
            elif type == "summary":
                evaluate_item["summary"] = value
        # 解析 评分
        evaluate_item["total"] = content.xpath(".//div[@class='score clearfix']/span/text()").extract_first()
        grades = content.xpath(".//div[@class='single-score']/p/span")
        for grade in grades:
            type = grade.xpath("./text()").extract_first().encode("utf-8")
            value = grade.xpath("./em/text()").extract_first()
            if type == "性价比：":
                evaluate_item["cost"] = value
            elif type == "性能：":
                evaluate_item["property"] = value
            elif type == "续航：":
                evaluate_item["endurance"] = value
            elif type == "外观：":
                evaluate_item["appearance"] = value
            elif type == "拍照：":
                evaluate_item["photograph"] = value
        # 解析 评论和点赞数
        evaluate_item["agree_num"] = content.xpath(".//a[@class='_j_review_vote']//text()").extract_first()
        evaluate_item["comment_num"] = content.xpath(".//a[@class='_j_review_reply']//text()").extract_first()
        item["evaluate_item"] = evaluate_item
        # print "item:"+str(item)
        return item

    # 解析单条评论详情页面
    def parse_comment_detail(self, response):
        # print "url:"+response.url
        # 从页面提取全部内容
        item = MobileItem()
        item["name"] = response.meta.get("mobileName")
        evaluate_item = EvaluateItem()
        evaluate_item["title"] = response.xpath("//h1[@class='title']/text()").extract_first()
        # 解析用户基本信息
        evaluate_item["name"] = response.xpath("//div[@class='user-info']/span[@class='name']/text()").extract_first()
        evaluate_item["position"] = response.meta.get("tag")
        # 解析 评论和点赞数
        evaluate_item["agree_num"] = response.xpath(".//span[@class='_j_vote_num']/text()").extract_first()
        evaluate_item["comment_num"] = response.xpath(".//div[@class='discuss-btn']//text()").extract_first()
        # 解析 购买信息
        shop_msgs = response.xpath(".//div[@class='comments-pro']/p")
        for shop_msg in shop_msgs:
            type = shop_msg.xpath("./text()").extract_first().encode("utf-8")
            value = shop_msg.xpath("./em/text()").extract_first()
            if type == "购买价格：":
                evaluate_item["price"] = value
            elif type == "购买时间：":
                evaluate_item["date"] = value
            elif type == "购买地点：":
                evaluate_item["place"] = value
        # 解析 评分
        evaluate_item["total"] = response.xpath(".//div[@class='total-score']/strong/text()").extract_first()
        grades = response.xpath(".//ul[@class='score-list clearfix']/li")
        for grade in grades:
            type = grade.xpath("./span[@class='label']/text()").extract_first().encode("utf-8")
            value = grade.xpath("./span[@class='score-num']/text()").extract_first()
            if type == "性价比":
                evaluate_item["cost"] = value
            elif type == "性能配置":
                evaluate_item["property"] = value
            elif type == "电池续航":
                evaluate_item["endurance"] = value
            elif type == "外观手感":
                evaluate_item["appearance"] = value
            elif type == "拍照效果":
                evaluate_item["photograph"] = value
        # 解析 优缺点
        advantage = ""
        merits = response.xpath("//div[@class='merits']//li/text()").extract()
        for merit in merits:
            advantage = advantage + merit + "\n"
        evaluate_item["advantage"] = advantage
        disadvantage = ""
        faults = response.xpath("//div[@class='faults']//li/text()").extract()
        for fault in faults:
            disadvantage = disadvantage + fault + "\n"
        evaluate_item["disadvantage"] = disadvantage
        # 解析 文章内容
        content = ""
        article_items = response.xpath("//div[@class='article-box']/div")
        for article_item in article_items:
            content = content + str(article_item.xpath(".//h4/text()").extract_first() or "") + "::"
            content = content + str(article_item.xpath(".//p/text()").extract_first() or "") + "\n"
        evaluate_item["content"] = content
        item["evaluate_item"] = evaluate_item
        yield item

    # 解析“查看更多”接口返回的数据
    # def parse_comment_more(self, response):
    #     comment_nums = int(response.xpath("//div[@class='total-num total-num-tip']/span/text()").extract_first()[:-3])
    #     pro_id = int(response.url.split("/")[-2])
    #     page_nums = (comment_nums + self.page_size - 1) / self.page_size
    #     for num in range(2, page_nums):
    #         ajax_url = "http://detail.zol.com.cn/xhr4_Review_GetList_proId="
    #         ajax_url += str(pro_id)+"%5Elevel=0%5Efilter=1%5Epage=";
    #         ajax_url += str(num)+".html";
    #         yield Request(url=ajax_url, callback=None)
    #     pass

    def parse_ajax_items(self, response):
        # print "url:"+response.url
        name = response.meta.get("name")
        json_body = json.loads(response.body)
        selector = Selector(text=json_body["list"])
        comments = selector.xpath("//div[@class='comments-item']")
        for comment in comments:
            yield self.parse_comment_item(comment, name)
        # print "response:"+json_body["list"]
        pass
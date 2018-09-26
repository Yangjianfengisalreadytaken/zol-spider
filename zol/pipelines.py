# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

from zol import settings


class ParamsPipeline(object):
    def __init__(self):
        # 连接数据库
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=3306,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            charset='utf8',
            use_unicode=True)
        # 通过cursor执行增删查改
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        if spider.name == "params":
            self.process_params(item)
        elif spider.name == "comments":
            self.process_comments(item)
        pass

    # 处理手机参数 item
    def process_params(self, item):
        try:
            # 查重处理
            self.cursor.execute(
                """select id from mobile where name = %s""",
                (item.get('base_msg').get('name')))
            # 是否有重复数据
            repetition = self.cursor.fetchone()
            # 重复
            if repetition:
                return

            mobile_id = self.save_base_msg(item.get("base_msg"))
            if mobile_id is -1:
                return
            self.save_params_screen(item.get("params_screen"), mobile_id)
            self.save_params_hardware(item.get("params_hardware"), mobile_id)
            self.save_params_network(item.get("params_network"), mobile_id)
            self.save_params_camera(item.get("params_camera"), mobile_id)
            self.save_params_appear(item.get("params_appear"), mobile_id)
            self.save_additional_func(item.get("addition_func"), mobile_id)
            self.save_guarantee(item.get("guarantee"), mobile_id)
            # 提交sql语句
            self.connect.commit()

            # 保存成功信息
            self.cursor.execute(
                """update mobile set success = '1' where id = %s""",
                (mobile_id))
            self.connect.commit()

        except Exception as error:
            # 出现错误时打印错误日志
            print "error:" + str(error)
        return item

    # 保存手机基础信息
    def save_base_msg(self, item):
        self.cursor.execute(
            """insert into mobile(name, brand, market_date,
                price, type, system, attachment, url)
            value (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (item.get('name'),
             item.get('brand'),
             item.get('market_date'),
             item.get('price'),
             item.get('type'),
             item.get('system'),
             item.get('attachment'),
             item.get('url')))
        # 提交sql语句
        self.connect.commit()

        # 获取并返回 mobile_id
        self.cursor.execute(
            """select id from mobile where name = %s""",
            (item['name']))
        mobile_id = self.cursor.fetchone()
        if mobile_id:
            return mobile_id[0]
        return -1
        pass

    # 保存屏幕参数
    def save_params_screen(self, item, mobile_id):
        if item is None:
            return
        self.cursor.execute(
            """insert into params_screen(mobile_id, type, size, texture,
                resolution, ppi, border, technology, ratio, others, vice_screen)
            value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (mobile_id,
             item.get('type'),
             item.get('size'),
             item.get('texture'),
             item.get('resolution'),
             item.get('ppi'),
             item.get('border'),
             item.get("technology"),
             item.get('ratio'),
             item.get('others'),
             item.get('vice_screen')))
        pass

    # 保存硬件参数
    def save_params_hardware(self, item, mobile_id):
        if item is None:
            return
        self.cursor.execute(
            """insert into params_hardware(mobile_id, cpu_type, cpu_fre, core_num,
                gpu_type, ram, rom, storage_card, extand_storage, battery_type, battery_size,
                employ_duration, charge_duration, others, phone_duration, await_duration, system)
            value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (mobile_id,
             item.get('cpu_type'),
             item.get('cpu_fre'),
             item.get('core_num'),
             item.get('gpu_type'),
             item.get('ram'),
             item.get('rom'),
             item.get('storage_card'),
             item.get('extand_storage'),
             item.get('battery_type'),
             item.get('battery_size'),
             item.get('employ_duration'),
             item.get('charge_duration'),
             item.get('others'),
             item.get('phone_duration'),
             item.get('await_duration'),
             item.get('system')))
        pass

    # 保存网络与连接参数
    def save_params_network(self, item, mobile_id):
        if item is None:
            return
        self.cursor.execute(
            """insert into params_network(mobile_id, network_4g, network_3g, frequency,
                sim_type, wlan, director, connect, connector, others)
            value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (mobile_id,
             item.get('network_4g'),
             item.get('network_3g'),
             item.get('frequency'),
             item.get('sim_type'),
             item.get('wlan'),
             item.get('director'),
             item.get('connect'),
             item.get('connector'),
             item.get('others')))
        pass

    # 保存摄像头参数
    def save_params_camera(self, item, mobile_id):
        if item is None:
            return
        self.cursor.execute(
            """insert into params_camera(mobile_id, count, background, foreground,
                sensor_type, flashlight, video, aperture, photo, feature, type, others, model)
            value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (mobile_id,
             item.get('count'),
             item.get('background'),
             item.get('foreground'),
             item.get('sensor_type'),
             item.get('flashlight'),
             item.get('video'),
             item.get('aperture'),
             item.get('photo'),
             item.get('feature'),
             item.get('type'),
             item.get('others'),
             item.get('item')))
        pass

    # 保存外观参数
    def save_params_appear(self, item, mobile_id):
        if item is None:
            return
        self.cursor.execute(
            """insert into params_appear(mobile_id, model, color, size,
                weight, texture, operate, fingerprint, connector, characters, others, inductor_type)
            value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (mobile_id,
             item.get('model'),
             item.get('color'),
             item.get('size'),
             item.get('weight'),
             item.get('texture'),
             item.get('operate'),
             item.get('fingerprint'),
             item.get('connector'),
             item.get('character'),
             item.get('others'),
             item.get('inductor_type')))
        pass

    # 保存更多功能与服务参数
    def save_additional_func(self, item, mobile_id):
        if item is None:
            return
        self.cursor.execute(
            """insert into additional_func(mobile_id, inductor_type, audio, video,
                picture, media, common_func, business_func, service, proofings, others)
            value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (mobile_id,
             item.get('inductor_type'),
             item.get('audio'),
             item.get('video'),
             item.get('picture'),
             item.get('media'),
             item.get('common_func'),
             item.get('business_func'),
             item.get('service'),
             item.get('proofings'),
             item.get('others')))
        pass

    # 保存保修信息参数
    def save_guarantee(self, item, mobile_id):
        if item is None:
            return
        self.cursor.execute(
            """insert into guarantee(mobile_id, policy, duration, note,
                phone, phone_note, details)
            value (%s, %s, %s, %s, %s, %s, %s)""",
            (mobile_id,
             item.get('policy'),
             item.get('duration'),
             item.get('note'),
             item.get('phone'),
             item.get('phone_note'),
             item.get('details')))
        pass

    # 处理评论 item
    def process_comments(self, item):
        try:
            # 获取并返回 mobile_id
            self.cursor.execute(
                """select id from mobile where name = %s""",
                (item['name']))
            mobile_id = self.cursor.fetchone()[0]
            self.save_total_comment(item.get("evaluate"), mobile_id)
            self.save_detail_comment(item.get("evaluate_item"), mobile_id)
            # 提交sql语句
            self.connect.commit()
        except Exception as error:
            # 出现错误时打印错误日志
            print "error:" + str(error)
            print 'item:' + str(item)
        pass

    def save_total_comment(self, item, mobile_id):
        if item is None:
            return
        # print str(item)
        self.cursor.execute(
            """insert into evaluate(mobile_id, total, cost, property,
                endurance, appearance, photograph, advantage, disadvantage)
            value (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (mobile_id,
             str(item.get('total')),
             str(item.get('cost')),
             str(item.get('property')),
             str(item.get('endurance')),
             str(item.get('appearance')),
             str(item.get('photograph')),
             item.get('advantage'),
             item.get('disadvantage')))
        pass

    def save_detail_comment(self, item, mobile_id):
        if item is None:
            return
        self.cursor.execute(
            """insert into evaluate_item(mobile_id, name, price, date,
                place, position, total, cost, property, endurance, appearance, photograph, 
                title, advantage, disadvantage, summary, content, comment_num, agree_num)
            value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (mobile_id,
             item.get('name'),
             item.get('price'),
             item.get('date'),
             item.get('place'),
             item.get('position'),
             str(item.get('total')),
             item.get('cost'),
             item.get('property'),
             item.get('endurance'),
             item.get('appearance'),
             item.get('photograph'),
             item.get('title'),
             item.get('advantage'),
             item.get('disadvantage'),
             item.get('summary'),
             item.get('content'),
             item.get('comment_num'),
             item.get('agree_num')))
        pass

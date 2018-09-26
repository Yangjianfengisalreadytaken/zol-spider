# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field, Item


class BrandItem(Item):
    id = Field()
    name = Field()
    description = Field()


class MobileItem(Item):
    name = Field()

    base_msg = Field()
    params_screen = Field()
    params_hardware = Field()
    params_network = Field()
    params_appear = Field()
    params_camera = Field()
    addition_func = Field()
    guarantee = Field()
    evaluate = Field()
    evaluate_item = Field()


class BaseMsg(Item):
    id = Field()
    name = Field()
    brand = Field()
    market_date = Field()
    price = Field()
    type = Field()
    system = Field()
    attachment = Field()
    date = Field()
    url = Field()
    success = Field()


class ParamsScreen(Item):
    type = Field()
    size = Field()
    texture = Field()
    resolution = Field()
    ppi = Field()
    border = Field()
    technology = Field()
    ratio = Field()
    others = Field()
    vice_screen = Field()


class ParamsHardware(Item):
    cpu_type = Field()
    cpu_fre = Field()
    core_num = Field()
    gpu_type = Field()
    ram = Field()
    rom = Field()
    storage_card = Field()
    extand_storage = Field()
    battery_type = Field()
    battery_size = Field()
    employ_duration = Field()
    charge_duration = Field()
    others = Field()
    phone_duration = Field()
    await_duration = Field()
    system = Field()


class ParamsNetwork(Item):
    network_4g = Field()
    network_3g = Field()
    frequency = Field()
    sim_type = Field()
    wlan = Field()
    director = Field()
    connect = Field()
    connector = Field()
    others = Field()


class ParamsCamera(Item):
    count = Field()
    background = Field()
    foreground = Field()
    sensor_type = Field()
    flashlight = Field()
    video = Field()
    aperture = Field()
    photo = Field()
    feature = Field()
    type = Field()
    others = Field()
    model = Field()


class ParamsAppear(Item):
    model = Field()
    color = Field()
    size = Field()
    weight = Field()
    texture = Field()
    operate = Field()
    fingerprint = Field()
    character = Field()
    connector = Field()
    others = Field()
    inductor_type = Field()


class AdditionalFunc(Item):
    inductor_type = Field()
    audio = Field()
    video = Field()
    picture = Field()
    media = Field()
    common_func = Field()
    business_func = Field()
    service = Field()
    proofings = Field()
    others = Field()


class Guarantee(Item):
    policy = Field()
    duration = Field()
    note = Field()
    phone = Field()
    phone_note = Field()
    details = Field()


class Evaluate(Item):
    total = Field()
    cost = Field()
    property = Field()
    endurance = Field()
    appearance = Field()
    photograph = Field()
    advantage = Field()
    disadvantage = Field()


class EvaluateItem(Item):
    name = Field()
    price = Field()
    date = Field()
    place = Field()
    position = Field()
    total = Field()
    cost = Field()
    property = Field()
    endurance = Field()
    appearance = Field()
    photograph = Field()
    title = Field()
    advantage = Field()
    disadvantage = Field()
    summary = Field()
    content = Field()
    comment_num = Field()
    agree_num = Field()













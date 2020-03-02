# -*- coding:utf-8 -*-
import re
import requests
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import os
from queue import Queue, Empty
import time
import json
import logging


def get_log():
    logging.basicConfig(filename="log.txt", format="[%(asctime)s] %(levelname)s: %(message)s", filemode="a+")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    return logger


def sign(name: str, headers, queue: Queue):
    """
    通过名字给贴吧签到
    :param name: 贴吧名字
    :return:
    """
    try:
        name = name.replace('\\\\', '\\').encode('latin-1').decode('unicode_escape')
        url = 'http://tieba.baidu.com/sign/add'
        form = {'ie': 'utf-8',
                'kw': name,  # 要签到的贴吧名
                'tbs': '9da208cc747e7b5b1519730458'}
        # html = requests.post(url, data=form, headers=headers).json()
        shuju = requests.post(url, data=form, headers=headers)
        html = shuju.json()
        if html['no'] == 1101:
            print('[' + name + '吧]:' + '亲，此贴吧您之前已经签过了哦!')
        if html['error'] == '' or html['no'] == 0:
            print('[' + name + '吧]:' + '签到成功!')
            # num += 1
            queue.put(name)
    except json.decoder.JSONDecodeError:
        # print(shuju.content)  # 等下改成日志
        # logger = get_log()
        # logger.error(shuju.content)
        return shuju.content
    pass


def main():
    logger=get_log()
    start = time.time()
    q = Queue()
    print('*' * 30 + '多线程百度贴吧签到小助手' + '*' * 30)
    with open("cookie.txt") as f:
        cookie = f.read()
    headers = {
        'Cookie': cookie,
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        'User-Agent': "baidubrowser / 042_1.8.4.2_diordna_008_084 / AIDIVN_01_4.3.2_608W / 1000591a / "
                      "9B673AC85965A58761CF435A48076629 % 7C880249110567268 / 1 "
    }
    url = 'https://tieba.baidu.com/'
    html = requests.get(url, headers=headers).text
    tieba = re.findall(r'forum_name":"(.*?)"', html)
    tieba = tieba[:int(len(tieba) / 2)]
    print('正在进行贴吧签到...')
    print("共有%d个吧" % len(tieba))
    num = 0
    with ThreadPoolExecutor(os.cpu_count() * 2) as tp:
        # tp.map(sign, tieba, len(tieba) * [headers], len(tieba) * [q], timeout=10)
        tasks = [tp.submit(sign, i, j, k) for i, j, k in
                 zip(tieba, len(tieba) * [headers], len(tieba) * [q])]  # 这里的task是一个未来对象
        result = wait(tasks, timeout=10, return_when=ALL_COMPLETED)
        for task in result.done:
            if task.result():
                logger.error(task.result())
    while True:
        try:
            q.get(block=False)
            num += 1
        except Empty:
            break
    print('\n')
    print('恭喜您,贴吧签到成功!一共签到' + str(num) + '个贴吧!')
    print("耗时%s秒" % (time.time() - start,))


if __name__ == "__main__":
    main()

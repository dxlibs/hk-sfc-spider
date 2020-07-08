#!/usr/bin/python3
import urllib.request
import urllib.parse
import json
import os
import time
import logging
import vars
import math
import codecs
import threading
import re

PROJECT_ROOT = os.getcwd()

logging.basicConfig(
    filename=PROJECT_ROOT+"/run.log",
    filemode="w+",
    level=logging.INFO,
    format='%(asctime)s - %(message)s')
LOG = logging.getLogger(__name__)

def get_user(role, ratype, letter, page):
    file = PROJECT_ROOT + '/json/{}_{}_{}_{}.json'.format(role, ratype, letter, page)
    url = "https://www.sfc.hk/publicregWeb/searchByRaJson?_dc=%d" % int(time.time()*1000)
    """
    roleType: individual|corporation
    """
    params = {
        "licstatus": "all",
        "ratype": ratype,
        "roleType": role,
        "nameStartLetter": letter,
        "page": page,
        "start": (page-1)*20,
        "limit": 20
    }
    params = urllib.parse.urlencode(params).encode('utf-8')

    headers = {
        'Host': 'www.sfc.hk',
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'User-Agent': vars.getUserAgent(),
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': "*/*",
        'Origin': '',
        'Origin': 'https://www.sfc.hk',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Length': len(params),
        'Cookie': "JSESSIONID=76D00F0A07B304D652E5A2EDDB26C197; TS0173272d=0126e39765daa947f95182cb2a914234612130296c7c51cd643b3cb0403f3d87a2b0da5d33d731484741dacc262e489b58349abd11; __utmz=23669880.1592967831.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=23669880.218372742.1592967831.1592967831.1593280674.2; __utmc=23669880; BIGipServerPOOL_APP_SFC_HTTPS=%3co%8exEaz%8c%ea%a8%bb%f0%ef%fd%88%07%3d%a9%d4%cc%b9%dc%bcr%c6%fe%3bP%ce%f0%154s%99%af%06%3b%14%e4%0b%1a%83%b9%de%e8%9c%e2%fd%0f%b4%ed%fbt%84%23%83%d8%d9%00%00%00%01; BIGipServerPOOL_SFC_HTTPS=v%dd%bd%3df'%c3%be%81%18%a0%f0%ef%fd%88%07%3d%a9%d4%cc%b9%dc%d9%054e%d5%09%83H%da%99%3e*%c5%e2%b4X%b4E5UDU%200%3e%3f%87YT%7c%fc7%e8%0a%c8%e60%00%00%00%01; TS019a838e=0126e39765049f06b3686551f4c96eb84aee2174b8f5706b7e7984729b6cae5f3b7645dd6d4bac74e0cd68ad92306a2e2cd4599923a4ffb8ce8699785c21ac34e1262ceafb"
    }

    try:
        req = urllib.request.Request(url, headers=headers, data=params)
        with urllib.request.urlopen(req) as response:
            if response.getcode() == 200:
                arr = json.loads(response.read())
                LOG.info("{}\t{}\t{}\t{}".format(ratype, file, 200, arr['totalCount']))
                if 'items' in arr:
                    with codecs.open(file, 'w+', encoding="utf-8") as fp_json:
                        json.dump(arr['items'], fp=fp_json, ensure_ascii=False)
                if page == 1 and arr['totalCount'] > 20:
                    for next_page in range(2, math.ceil(arr['totalCount']/20)+1):
                        next_file = PROJECT_ROOT + '/json/{}_{}_{}_{}.json'.format(role, ratype, letter, next_page)
                        if not os.path.exists(next_file):
                            get_user(role, ratype, letter, next_page)
            else:
                LOG.info("{}\t{}\t{}".format(ratype, file, response.getcode()))
    except OSError as err:
        LOG.info("{}\t{}\t{}".format(ratype, file, "Error", str(err)))


def get_page(ceref, page, file_id, retry_count=0):
    ceref_path = PROJECT_ROOT + '/page/{}'.format(ceref)
    if not os.path.exists(ceref_path):
        os.mkdir(ceref_path)
    page_arr = page.split("_", 1)
    file = ceref_path + '/{}.json'.format(page_arr[1])
    url = "https://www.sfc.hk/publicregWeb/{}/{}/{}".format(page_arr[0], ceref, page_arr[1])

    params = {}
    params = urllib.parse.urlencode(params).encode('utf-8')

    headers = {
        'Host': 'www.sfc.hk',
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'User-Agent': vars.getUserAgent(),
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'text/html;charset=UTF-8',
        'Accept': "*/*",
        'Origin': '',
        'Origin': 'https://www.sfc.hk',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Content-Length': len(params),
        'Cookie': "JSESSIONID=76D00F0A07B304D652E5A2EDDB26C197; TS0173272d=0126e39765daa947f95182cb2a914234612130296c7c51cd643b3cb0403f3d87a2b0da5d33d731484741dacc262e489b58349abd11; __utmz=23669880.1592967831.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=23669880.218372742.1592967831.1592967831.1593280674.2; __utmc=23669880; BIGipServerPOOL_APP_SFC_HTTPS=%3co%8exEaz%8c%ea%a8%bb%f0%ef%fd%88%07%3d%a9%d4%cc%b9%dc%bcr%c6%fe%3bP%ce%f0%154s%99%af%06%3b%14%e4%0b%1a%83%b9%de%e8%9c%e2%fd%0f%b4%ed%fbt%84%23%83%d8%d9%00%00%00%01; BIGipServerPOOL_SFC_HTTPS=v%dd%bd%3df'%c3%be%81%18%a0%f0%ef%fd%88%07%3d%a9%d4%cc%b9%dc%d9%054e%d5%09%83H%da%99%3e*%c5%e2%b4X%b4E5UDU%200%3e%3f%87YT%7c%fc7%e8%0a%c8%e60%00%00%00%01; TS019a838e=0126e39765049f06b3686551f4c96eb84aee2174b8f5706b7e7984729b6cae5f3b7645dd6d4bac74e0cd68ad92306a2e2cd4599923a4ffb8ce8699785c21ac34e1262ceafb"
    }

    try:
        req = urllib.request.Request(url, headers=headers, data=params)
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.getcode() == 200:
                html = str(response.read(), 'utf-8')
                json_str = get_vars_from_js(page, html)
                LOG.info("{}\t{}\t{}".format(file_id, url, len(json_str)))
                with codecs.open(file, 'w+', encoding="utf-8") as fp_json:
                    fp_json.write(json_str)
            else:
                LOG.info("{}\t{}\t{}".format(file_id, url, response.getcode()))
    except OSError as err:
        LOG.info("{}\t{}\t{}:{}\t{}".format(file_id, url, "Error", retry_count, str(err)))
        retry_count += 1
        if retry_count <5:
            get_page(ceref, page, file_id, retry_count)

def get_vars_from_js(page, html):
    html = str(html)
    patterns = {
        'indi_details': re.compile(r"var indData = (.*)];", re.MULTILINE),
        'indi_addresses': re.compile(r"var indData = (.*)];", re.MULTILINE),
        'indi_conditions': re.compile(r"var indData = (.*)];", re.MULTILINE),
        'indi_disciplinaryAction': re.compile(r"var disRemarkData = (.*)];", re.MULTILINE),
        'indi_licenceRecord': re.compile(r"var licRecordData = (.*)];", re.MULTILINE),
        'corp_details': re.compile(r"var raDetailData = (.*)];", re.MULTILINE),
        'corp_addresses': {
            'address': re.compile(r"var addressData = (.*)];", re.MULTILINE),
            'email': re.compile(r"var emailData = (.*)];", re.MULTILINE),
            'web': re.compile(r"var websiteData = (.*)];", re.MULTILINE)
        },
        'corp_ro': re.compile(r"var roData = (.*)];", re.MULTILINE),
        'corp_rep': re.compile(r"var repData = (.*)];", re.MULTILINE),
        'corp_co': re.compile(r"var cofficerData = (.*)];", re.MULTILINE),
        'corp_conditions': re.compile(r"var condData = (.*)];", re.MULTILINE),
        'corp_da': re.compile(r"var disRemarkData = (.*)];", re.MULTILINE),
        'corp_prev_name': re.compile(r"var prevNameData = (.*)];", re.MULTILINE),
        'corp_licences': re.compile(r"var licRecordData = (.*)];", re.MULTILINE)
    }
    pattern = patterns[page]

    if page == 'corp_addresses':
        ret = {}
        for key, patt in pattern.items():
            matches = re.findall(patt, html)
            if matches:
                ret[key] = json.loads(matches[0] + "]")
            else:
                ret[key] = []
        return json.dumps(ret)
    else:
        matches = re.findall(pattern, html)
        return matches[0] + "]" if matches else '[]'

def multi_process_user(type):
    letters = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
        'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
    ]
    for role in ['individual', 'corporation']:
        for letter in letters:
            get_user(role, type, letter, 1)

def multi_process_page(type, file_id):
    page_indi = ['indi_details', 'indi_addresses', 'indi_conditions', 'indi_disciplinaryAction', 'indi_licenceRecord']
    page_corp= ['corp_details', 'corp_addresses', 'corp_ro', 'corp_rep', 'corp_co', 'corp_conditions',
                         'corp_da', 'corp_prev_name', 'corp_licences']
    pages = page_indi if type == 'indi' else page_corp
    file = PROJECT_ROOT + '/user/{}_{}.txt'.format(type, file_id)
    with open(file, 'r') as fp:
        for line in fp.readlines():
            ceref = line.strip()
            for page in pages:
                get_page(ceref, page, file_id)

def run():
    # for i in range(11):
    #     t = threading.Thread(target=multi_by_type, args=(i, ))
    #     # t.daemon = True
    #     t.start()
    for i in range(22):
        t = threading.Thread(target=multi_process_page, args=('indi', i))
        t.start()

def test():
    html = """
    aaa
    """
    pattern = re.compile(r"var raDetailData = (.*)?];", re.MULTILINE)
    results = re.findall(pattern, html)
    print(results, type(results[0]))
    print(len(results))

if __name__ == '__main__':
    # parse.parse_corp()
    # parse.parse_indi()
    # test()
    # exit()
    for i in range(11):
        t = threading.Thread(target=multi_process_page, args=('corp', i))
        t.start()


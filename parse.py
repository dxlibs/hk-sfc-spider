#!/usr/bin/python3
# coding=utf-8

import json
import os
import glob
import time
import logging
import redis
from dbtool import dbtool

PROJECT_ROOT = os.getcwd()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s')
LOG = logging.getLogger(__name__)

r = redis.StrictRedis()

def parse_indi():
    """
    : 1. 清空数据库
    : 2. 逐个录入
    :return:
    """
    db = dbtool()
    db.clear_table('individuals')
    db.clear_table('individuals_licences')
    db.clear_table('individuals_conditions')
    db.clear_table('individuals_details')

    file = PROJECT_ROOT + '/indi.txt'
    pages = ['details', 'addresses', 'conditions', 'disciplinaryAction', 'licenceRecord']
    with open(file, 'r') as fp:
        for line in fp.readlines():
            ceref = line.strip()
            cache_key = "ceref_%s" % ceref
            single = json.loads(r.get(cache_key))
            if not single['isIndi']:
                continue
            letter = str(ceref)[:1].upper()
            indi_insert_data = {
                "letter": letter,
                "ceref": ceref,
                "name": single['name'] if single['name'] else '',
                "nameChi": single['nameChi'] if single['nameChi'] else '',
                "licence_date": "",
                "remarks": "",
                "status": 1 if single['hasActiveLicence'] == 'Y' else 0
            }
            for page in pages:
                page_file = "{}/page_indi/{}/{}.json".format(PROJECT_ROOT, ceref, page)
                with open(page_file, 'r', encoding='utf-8') as fp:
                    arr = json.load(fp)
                    if page == 'details' and arr:
                        details_insert_data = []
                        for row in arr:
                            role = row["lcRole"] if row["lcRole"] else ''
                            role_name = ''
                            if role:
                                role_name ="代表" if row["lcRole"] == "RE" else '負責人員'
                            details_insert_data.append({
                                "corp": row["prinCeRef"] if row["prinCeRef"] else '',
                                "indi": ceref,
                                "accStatus": row["accStatus"] if row["accStatus"] else '',
                                "accDate": utc2time(row["accDate"]),
                                "actType": row["actType"],
                                "actDate": utc2time(row["actDate"]),
                                "actDesc": row["actDesc"],
                                "actDescChi": row["actDescChi"],
                                "actStatus": row["actStatus"],
                                "role": role,
                                "role_name": role_name,
                                "role_date": utc2time(row["rrpDate"])
                            })
                        db.insert_batch('individuals_details', details_insert_data)
                        pass

                    if page == 'addresses' and arr:
                        pass

                    if page == 'conditions' and arr:
                        conditions_insert_data = []
                        for row in arr:
                            conditions_insert_data.append({
                                "ceref": ceref,
                                "effDate": utc2time(row["effDate"]),
                                "condition": row["conditionDtl"],
                                "conditionChi": row["conditionCDtl"],
                                "applNo": row["applNo"],
                                "lcSeqNo": row["lcSeqNo"]
                            })
                        db.insert_batch('individuals_conditions', conditions_insert_data)
                        pass

                    if page == 'disciplinaryAction' and arr:
                        da_insert_data = []
                        doc_url = "https://www.sfc.hk/publicregWeb/displayFile?docno=%s"
                        for row in arr:
                            da_insert_data.append({
                                "ceref": ceref,
                                "actDate": utc2time(row["actnDate"]),
                                "codeDesc": row["codeDesc"],
                                "codeDescChi": row["codeCdesc"],
                                "docEng": doc_url % row["engDocSeq"] if row["engDocSeq"] else '',
                                "docChi": doc_url % row["chiDocSeq"] if row["chiDocSeq"] else '',
                            })
                        db.insert_batch('individuals_da', da_insert_data)
                        pass

                    if page == 'licenceRecord' and arr:
                        license_insert_data = []
                        for row in arr:
                            if single['hasActiveLicence'] == 'Y' and not indi_insert_data['licence_date'] and row["effectivePeriodList"][0]["effectiveDate"]:
                                indi_insert_data['licence_date'] = utc2time(row["effectivePeriodList"][0]["effectiveDate"])
                            lt = row["lcType"] if row["lcType"] else ''
                            lt_name = ''
                            if lt:
                                lt_name = "註冊機構" if row["lcType"] == "E" else "持牌法團"
                            role = row["lcRole"] if row["lcRole"] else ''
                            role_name = ''
                            if role:
                                role_name = "代表" if row["lcRole"] == "RE" else '負責人員'
                            license_insert_data.append({
                                "indi": ceref,
                                "corp": row["prinCeRef"] if row["prinCeRef"] else '',
                                "role": role,
                                "role_name": role_name,
                                "licence_type": lt,
                                "licence_type_name": lt_name,
                                "actType": row["regulatedActivity"]["actType"],
                                "actDesc": row["regulatedActivity"]["actDesc"],
                                "actDescChi": row["regulatedActivity"]["cactDesc"],
                                "effDate": utc2time(row["effectivePeriodList"][0]["effectiveDate"]),
                                "endDate": utc2time(row["effectivePeriodList"][0]["endDate"]),
                                "status": 1 if row["regulatedActivity"]["status"] == "A" else 0,
                            })
                        db.insert_batch('individuals_licences', license_insert_data)
                        pass

            db.insert('individuals', indi_insert_data)

def parse_corp():
    """
    : 1. 录入Redis
    : 2. 清空数据库
    : 3. 逐个录入
    :return:
    """

    db = dbtool()
    db.clear_table('corporations')
    db.clear_table('corporations_licences')
    db.clear_table('corporations_ro')
    db.clear_table('corporations_rep')
    db.clear_table('corporations_co')
    db.clear_table('corporations_conditions')
    db.clear_table('corporations_da')
    db.clear_table('corporations_previous')

    status_map = {
        'A': '',
        'S': '被暫時吊銷牌照',
        'U': '負責人員的核准被暫時吊銷'
    }

    file = PROJECT_ROOT + '/corp.txt'
    pages = ['details', 'addresses', 'ro', 'rep', 'co', 'conditions', 'da', 'prev_name', 'licences']
    with open(file, 'r') as fp:
        for line in fp.readlines():
            ceref = line.strip()
            cache_key = "ceref_%s" % ceref
            single = json.loads(r.get(cache_key))

            letter = str(ceref)[:1].upper()
            corp_insert_data = {
                "letter": letter,
                "ceref": ceref,
                "name": single['name'] if single['name'] else '',
                "nameChi": single['nameChi'] if single['nameChi'] else '',
                "address": "",
                "addressChi": "",
                "licence_date": "",
                "remarks": "",
                "email": "",
                "website": "",
                "licence_status": 1 if single['hasActiveLicence'] == "Y" else 0
            }
            for page in pages:
                page_file = "{}/page_corp/{}/{}.json".format(PROJECT_ROOT, ceref, page)
                with open(page_file, 'r', encoding='utf-8') as fp:
                    arr = json.load(fp)
                    if page == 'details' and arr:
                        if arr[0]['effDate'] and arr[0]['endDate'] is None:
                            corp_insert_data['licence_date'] = utc2time(arr[0]['effDate'])
                    if page == 'prev_name' and arr:
                        prev_name_insert_data = []
                        for row in arr:
                            prev_name_insert_data.append({
                                "ceref": ceref,
                                "changeDate": utc2time(row["changeDate"]),
                                "englishName": row["englishName"] if row["englishName"] else '',
                                "chineseName": row["chineseName"] if row["chineseName"] else '',
                                "surname": row["surname"] if row["surname"] else '',
                                "otherName": row["otherName"] if row["otherName"] else '',
                            })
                        db.insert_batch('corporations_previous', prev_name_insert_data)
                        pass

                    if page == 'da' and arr:
                        da_insert_data = []
                        doc_url = "https://www.sfc.hk/publicregWeb/displayFile?docno=%s"
                        for row in arr:
                            da_insert_data.append({
                                "ceref": ceref,
                                "actDate": utc2time(row["actnDate"]),
                                "codeDesc": row["codeDesc"],
                                "codeDescChi": row["codeCdesc"],
                                "docEng": doc_url % row["engDocSeq"] if row["engDocSeq"] else '',
                                "docChi": doc_url % row["chiDocSeq"] if row["chiDocSeq"] else '',
                            })
                        db.insert_batch('corporations_da', da_insert_data)
                        pass

                    if page == 'conditions' and arr:
                        conditions_insert_data = []
                        for row in arr:
                            conditions_insert_data.append({
                                "ceref": ceref,
                                "effDate": utc2time(row["effDate"]),
                                "condition": row["conditionDtl"],
                                "conditionChi": row["conditionCDtl"],
                                "applNo": row["applNo"],
                                "lcSeqNo": row["lcSeqNo"]
                            })
                        db.insert_batch('corporations_conditions', conditions_insert_data)
                        pass

                    if page == 'ro' and arr:
                        ro_insert_data = []
                        for row in arr:
                            ro_insert_data.append({
                                'corp': ceref,
                                'indi': row['ceRef']
                            })
                        db.insert_batch('corporations_ro', ro_insert_data)
                        pass

                    if page == 'co' and arr:
                        co_insert_data = []
                        for row in arr:
                            co_insert_data.append({
                                'ceref': ceref,
                                'tel': row['tel'] if row['tel'] else '',
                                'fax': row['fax'] if row['fax'] else '',
                                'email': row['email'] if row['email'] else '',
                                'address': row['address']['fullAddress'] if row['address']['fullAddress'] else '',
                                'addressChi': row['address']['fullAddressChin'] if row['address']['fullAddressChin'] else ''
                            })
                        db.insert_batch('corporations_co', co_insert_data)
                        pass

                    if page == 'rep' and arr:
                        rep_insert_data = []
                        for row in arr:
                            rep_insert_data.append({
                                'corp': ceref,
                                'indi': row['ceRef']
                            })
                        db.insert_batch('corporations_rep', rep_insert_data)
                        pass

                    if page == 'licences' and arr:
                        license_insert_data = []
                        for row in arr:
                            lt = row["lcType"] if row["lcType"] else ''
                            lt_name = ''
                            if lt:
                                lt_name = "註冊機構" if row["lcType"] == "E" else "持牌法團"
                            license_insert_data.append({
                                "ceref": ceref,
                                "licence_type": lt,
                                "licence_type_name": lt_name,
                                "actType": row["regulatedActivity"]["actType"],
                                "actDesc": row["regulatedActivity"]["actDesc"],
                                "actDescChi": row["regulatedActivity"]["cactDesc"],
                                "effDate": utc2time(row["effectivePeriodList"][0]["effectiveDate"]),
                                "endDate": utc2time(row["effectivePeriodList"][0]["endDate"]),
                                "status": 1 if row["regulatedActivity"]["status"] == "A" else 0,
                            })
                        db.insert_batch('corporations_licences', license_insert_data)
                        pass

                    if page == 'addresses':
                        if arr['address'] and arr['address'][0]:
                            corp_insert_data['address'] = arr['address'][0]['fullAddress']
                            corp_insert_data['addressChi'] = arr['address'][0]['fullAddressChin']
                        if arr['email'] and arr['email'][0]:
                            corp_insert_data['email'] = arr['email'][0]['email']
                        if arr['web'] and arr['web'][0]:
                            corp_insert_data['website'] = arr['web'][0]['website']

            db.insert('corporations', corp_insert_data)
    del db

def utc2time(time_str, format="%Y-%m-%d"):
    if not time_str:
        return ''
    time_tuple = time.strptime(time_str, "%b %d, %Y %H:%M:%S %p")
    return time.strftime(format, time_tuple)


def init_redis():
    for file in glob.glob(PROJECT_ROOT + '/json/*.json'):
        with open(file, 'r',  encoding='utf-8') as fp:
            arr = json.load(fp)
            if arr:
                for row in arr:
                    ceref = row['ceref']
                    cache_key = "ceref_%s" % ceref
                    if not r.get(cache_key):
                        r.set(cache_key, json.dumps(row), 86400)


if __name__ == '__main__':
    LOG.info("Redis Start")
    #init_redis()
    LOG.info("Corp Start")
    #parse_corp()
    LOG.info("Indi Start")
    parse_indi()
    LOG.info("All End")

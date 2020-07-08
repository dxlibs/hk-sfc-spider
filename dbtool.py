#!/usr/bin/python3

import pymysql
from pymysql.cursors import DictCursor
import os
import logging

PROJECT_ROOT = os.getcwd()

logging.basicConfig(
    filename=PROJECT_ROOT+"/sql.log",
    filemode="w+",
    level=logging.INFO,
    format='%(asctime)s - %(message)s')
LOG = logging.getLogger(__name__)

class dbtool():
    conn = None
    cursor = None

    def __init__(self, *args, **kwargs):
        self.connect()

    def connect(self):
        if not self.conn:
            self.conn = pymysql.connect(
                host='localhost',
                user='root',
                passwd='develop',
                db='sfc',
                charset='utf8mb4'
            )
        if not self.cursor:
            self.cursor = self.conn.cursor(DictCursor)
            sql = "SET NAMES utf8;"
            self.cursor.execute(sql)
        return


    def set_where(self, where_and=[], where_or=[]):
        pass

    def get_row(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchone(sql)

    def get_all(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall(sql)

    def insert_batch(self, table, data):
        columns = []
        values = []
        for i in range(len(data)):
            value = []
            for key, val in data[i].items():
                if i == 0:
                    columns.append("`{}`".format(key))
                value.append("{}".format(self.conn.escape(val)))
            values.append("("+", ".join(value)+")")

        sql = "INSERT INTO {}({}) VALUES{};".format(table, ", ".join(columns), ", ".join(values))
        # LOG.info(sql.replace(u'\xa0 ', u' '))
        self.cursor.execute(sql)
        self.conn.commit()

    def insert(self, table, data):
        columns = []
        values = []
        for key, val in data.items():
            columns.append("`{}`".format(key))
            values.append("{}".format(self.conn.escape(val)))
        sql = "INSERT INTO {}({}) VALUES({});".format(table, ", ".join(columns), ", ".join(values))
        # LOG.info(sql.replace(u'\xa0 ', u' '))
        self.cursor.execute(sql)
        self.conn.commit()
        lastrowid = self.cursor.lastrowid
        return lastrowid

    def clear_table(self, table):
        sql = "TRUNCATE {};".format(table)
        self.cursor.execute(sql)
        self.conn.commit()

    def __del__(self):
        if self.cursor:
            self.cursor.close()
        if self.cursor:
            self.conn.close()



import pymysql
import json
import requests
import urllib2
import time

sql = """UPDATE s_articles_details SET laststock=%s WHERE id=%s"""

epilog_sql1 = "DELETE FROM s_articles_a"
epilog_sql2 = "INSERT INTO s_articles_a(articleID, s, c) SELECT d.articleID, SUM(laststock) s, COUNT(*) c FROM s_articles_details d GROUP BY d.articleID"
epilog_sql3 = "DELETE FROM s_articles_a WHERE c=1"
epilog_sql4 = "UPDATE s_articles SET laststock=0 WHERE id IN (SELECT articleID FROM s_articles_a WHERE c>s)"
epilog_sql5 = "UPDATE s_articles SET laststock=1 WHERE id IN (SELECT articleID FROM s_articles_a WHERE c=s)"

HEADER = {'Content-Type': 'application/json'}

active_check = {"T":0, "F":1}

supplierNumberID = 0
deeplinkID = 7

data_dir = '/var/www/vhosts/my-mik.de/Sourcing_File/'
ac_file_list = ['shop_ac.csv', 'amazon_ac.csv']
inac_file_list = ['shop_inac.csv', 'amazon_inac.csv']

def update_inven(filename, ac):
    conn = pymysql.connect(host='localhost', user=user, password=password, db=db, charset='utf8')
    f = open(data_dir+filename, 'r')
    for article in f.readlines():
        spn = article.split(',')[0]
        vid = article.split(',')[1].replace('\n', '')

        with conn.cursor() as curs:
            curs.execute(sql, (ac, vid))
            conn.commit()
    f.close()
    conn.close()

def update_epilog():
    conn = pymysql.connect(host='localhost', user=user, password=password, db=db, charset='utf8')
    with conn.cursor() as curs:
        curs.execute(epilog_sql1)
        conn.commit()
    with conn.cursor() as curs:
        curs.execute(epilog_sql2)
        conn.commit()
    with conn.cursor() as curs:
        curs.execute(epilog_sql3)
        conn.commit()
    with conn.cursor() as curs:
        curs.execute(epilog_sql4)
        conn.commit()
    with conn.cursor() as curs:
        curs.execute(epilog_sql5)
        conn.commit()
    conn.commit()

def update_active(conn, active, variantID):
    with conn.cursor() as curs:
        curs.execute(sql, (active, variantID))
        conn.commit()


if __name__ == "__main__":
    update_inven(inac_file_list[1], 1)
    update_inven(ac_file_list[1], 0)
    #update_epilog()


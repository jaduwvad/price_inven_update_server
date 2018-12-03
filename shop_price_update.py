import pymysql
import time
import os
import urllib2

data_dir = "/var/www/vhosts/my-mik.de/Sourcing_File/"

supplierNumberID = 0
variantidID = 1
priceID = 2

tax_rate_list = {"1":1.19, "4":1.07, "5":1}

sql_for_details = """UPDATE s_articles_details SET purchaseprice=%s WHERE id=%s"""
sql_for_price = """UPDATE s_articles_prices SET price=%s WHERE articledetailsID=%s"""
sql_for_tax = """SELECT taxID FROM s_articles WHERE id=(SELECT articleID FROM s_articles_details WHERE id=%s)"""
sql_for_date = """UPDATE s_articles_attributes SET attr2=%s WHERE articledetailsID=%s"""

def update_details(conn, price, variantid):
    with conn.cursor() as curs:
        curs.execute(sql_for_details, (price, variantid))
        conn.commit()

def get_tax_rate(conn, variantid):
    try:
        with conn.cursor() as curs:
            curs.execute(sql_for_tax, variantid)
            return curs.fetchall()[0][0]
    except:
        return False

def update_price(conn, price, variantid):
    with conn.cursor() as curs:
        curs.execute(sql_for_price, (price, variantid))
        conn.commit()
        
def update_date(conn, variantid):
    now = time.localtime()
    datestamp = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    with conn.cursor() as curs:
        curs.execute(sql_for_date, (datestamp, variantid))
        conn.commit()

def update_process(data_file):
    conn = pymysql.connect(host='localhost', user=user,password=password, db = db, charset='utf8')
    f = open(data_dir+data_file, "r")

    for an in f.readlines():
        attr = an.split(',')
        try:
            if data_file == 'wave_price.csv':
                price_without_tax = float(attr[priceID])/1.19*1.08
            else:
                tax_rate = get_tax_rate(conn, attr[variantidID])
                if tax_rate is False:
                    continue
                price_without_tax = float(attr[priceID])/tax_rate_list[str(tax_rate)]
        except ValueError:
            continue

        update_details(conn, attr[priceID].replace("\n", ''), attr[variantidID])
        update_price(conn, '%.2f'%price_without_tax, attr[variantidID])
        update_date(conn, attr[variantidID])

    f.close()
    conn.close()

if __name__ == "__main__":
    update_process('article_price.csv')
    update_process('alternate_price.csv')
    update_process('wave_price.csv')
    update_process('amazon_price.csv')




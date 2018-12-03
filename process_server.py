from socket import *
from os import fork
import threading
import logging

HOST = ''
PORT = port
BUFSIZE = 1024
ADDR = (HOST, PORT)

AC_SIGN = 0
INAC_SIGN = 1

price_file_list = ['article_price.csv', 'alternate_price.csv', 'amazon_price.csv', 'wave_price.csv']
inven_ac_file_list = ['shop_ac.csv', 'alternate_ac.csv', 'amazon_ac.csv', 'wave_ac.csv']
inven_inac_file_list = ['shop_inac.csv', 'alternate_inac.csv', 'amazon_inac.csv', 'wave_inac.csv']
shop_list = {'shops':0, 'alternate':1, 'amazon':2, 'wave':3}

client_ip = ''

logging.basicConfig(filename='/var/log/mymik/server_log', format='[%(asctime)s] %(name)s [%(levelname)s] %(message)s', level=logging.INFO)

def update_price(shop):
    shop_number = int(shop)
    import shop_price_update
    shop_price_update.update_process(price_file_list[shop_number])
    logging.info('PRICE - ' +  shop_list.keys()[shop_number].upper() + ' - ' + price_file_list[shop_number] + ' updated')

def update_inven(shop):
    shop_number = int(shop)
    import inven_update
    inven_update.update_inven(inven_ac_file_list[shop_number], AC_SIGN)
    logging.info('INVEN - ' + shop_list.keys()[shop_number].upper() + ' - ' + inven_ac_file_list[shop_number] + ' updated')
    inven_update.update_inven(inven_inac_file_list[shop_number], INAC_SIGN)
    logging.info('INVEN - ' + shop_list.keys()[shop_number].upper() + ' - ' + inven_inac_file_list[shop_number] + ' updated')

    if shop_number == 0:
        logging.getLogger().setLevel(logging.WARN)
        logging.getLogger().setLevel(logging.INFO)

    inven_update.update_epilog()
    logging.info('INVEN - Inventory Update Epilog Done')


def update_index():
    import index_update
    logging.getLogger().setLevel(logging.WARN)
    index_update.update()
    logging.getLogger().setLevel(logging.INFO)
    logging.info('INDEX - Update Complete')

def set_orders():
    import set_orders
    set_orders.make_files()
    logging.info('ORDER - Making File Complete')

def main():
    server_socket = socket(AF_INET,SOCK_STREAM)
    server_socket.bind(ADDR)

    logging.info("SERVER - Server Binded")

    while True:
        server_socket.listen(100)
        client_socket, addr_info = server_socket.accept()
        if addr_info[0] != client_ip:
            p_logger.error("SERVER - Access Denied : " + addr_info[0])
            continue

        logging.info('SERVER - Access Success : ' + addr_info[0])
        update_kind = client_socket.recv(65536)

        t = threading.Thread()

        if update_kind == 'price':
            shop_kind = client_socket.recv(65536)
            logging.info('SERVER - Get Signal %s %s'% (update_kind, shop_kind))
            t = threading.Thread(target=update_price, args=(str(shop_list[shop_kind])))
        elif update_kind == 'inven':
            shop_kind = client_socket.recv(65536)
            logging.info('SERVER - Get Signal %s %s'% (update_kind, shop_kind))
            t = threading.Thread(target=update_inven, args=(str(shop_list[shop_kind])))
        elif update_kind == 'index':
            logging.info('SERVER - Get Signal %s'% update_kind)
            t = threading.Thread(target=update_index, args = ())
        elif update_kind == 'order':
            logging.info('SERVER - Get Signal %s'% update_kind)
            t = threading.Thread(target=set_orders, args=())
        elif update_kind == 'end':
            logging.info('SERVER - Recieved Terminate Signal')
            break

        try:
            t.start()
        except KeyboardInterrupt:
            logging.info('SERVER - Keyboard Terminate Signal')
            break

    client_socket.close()
    server_socket.close()
    logging.info('SERVER - Server Terminated')

if __name__=="__main__":
    if fork() > 0:
        exit(1)
    else:
        main()


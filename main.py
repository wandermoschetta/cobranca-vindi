from cobranca_vindi.scripts.cobranca import add, update_bills as update, remove_bills as remove
import time
from datetime import datetime


def main():
    while True:
        data_agora = datetime.now()

        print("")
        print("Aguardando 10 secs para começar processo.")
        time.sleep(10)
        print("")
        print("Inicio em: {}".format(data_agora.__str__()[:19]))
        print("")
        print("*******************************************")
        add()
        update()
        remove()
        print("")
        print("*******************************************")
        print("")


if __name__ == '__main__':
    main()

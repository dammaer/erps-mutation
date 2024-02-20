import time
from configparser import ConfigParser, NoSectionError
from hashlib import md5

from parse import Parse
from telnet import CFG
from commands import hw_l3


def ini():
    config = ConfigParser()
    config.read('settings.ini')
    try:
        urls = config.get('admin_urls', 'urls').split()
        login = config.get('authorization', 'login')
        passwd = config.get('authorization', 'passwd')
    except NoSectionError:
        login = input('Логин от админки> ')
        passwd = md5(input('Пароль от админки> ').encode()).hexdigest()
        config.add_section('authorization')
        config.set('authorization', 'login', login)
        config.set('authorization', 'passwd', passwd)
        with open('settings.ini', 'w') as f:
            config.write(f)
    return urls, login, passwd


def print_l3_config(ring_params):
    ring_id = int(input('Свободный ring_id (если это первое erps кольцо на l3, то введите 1)> '))
    first_ring = True if ring_id == 1 else False
    print(f'\n{hw_l3(ring_params, ring_id, first_ring)}\n')


def mutation(ring_id):
    ring_params, ring = Parse(*ini(), ring_id).get_data()
    raps_vlan = ring_params[1]
    if any(len(p['ports']) == 2 for p in ring):
        print('Ring is OK!')
        print_l3_config(ring_params)
        print('Если настроки верны, скопируйте конфиг на l3 и нажмите Enter для продолжения настройки кольца!')
        while input() != '':
            time.sleep(1)
        for swi in ring:
            print(f"{swi['l2_sw_ip']} - {swi['ports']}")
            if swi.get('owner'):
                print(f"{swi['l2_sw_ip']} - owner configuration...")
                CFG(raps_vlan, swi).owner()
            CFG(raps_vlan, swi).common()
            time.sleep(3)
        print(f'Ring {ring_id} - ERPS ON!')
    else:
        print('Ring NOT OK!')


if __name__ == "__main__":
    mutation(378)

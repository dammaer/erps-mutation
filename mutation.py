from parse import Parse
from telnet import CFG
import time


def mutation(adm_urls, adm_login, adm_passw, ring_id):
    raps_vlan, ring = Parse(adm_urls, adm_login, adm_passw, ring_id).get_data()
    owner = None
    if any(len(p['ports']) == 2 for p in ring):
        print('Ring is OK!')
        for swi in ring:
            print(f"{swi['l2_sw_ip']} - {swi['ports']}")
            CFG(swi['l2_sw_ip'], swi['auth'], swi['model'], raps_vlan, swi['ports']).copy()
            if swi.get('owner'):
                owner = swi
            time.sleep(3)
        print('Owner configuration...')
        CFG(owner['l2_sw_ip'], owner['auth'], owner['model'], raps_vlan, owner['ports']).SNR_owner()
        print(f'Ring {ring_id} - ERPS ON!')
    else:
        print('Ring NOT OK!')


if __name__ == "__main__":
    from configparser import ConfigParser, NoSectionError
    from hashlib import md5
    config = ConfigParser()
    config.read('settings.ini')
    try:
        URLS = config.get('admin_urls', 'urls').split()
        LOGIN = config.get('authorization', 'LOGIN')
        PASSWD = config.get('authorization', 'PASSWD')
    except NoSectionError:
        LOGIN = input('Логин от админки> ')
        PASSWD = md5(input('Пароль от админки> ').encode()).hexdigest()
        config.add_section('authorization')
        config.set('authorization', 'LOGIN', LOGIN)
        config.set('authorization', 'PASSWD', PASSWD)
        with open('settings.ini', 'w') as f:
            config.write(f)
    mutation(URLS, LOGIN, PASSWD, 138)

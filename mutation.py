import time
from configparser import ConfigParser, NoSectionError
from hashlib import md5

import commands as cmd
from parse import Parse
from telnet import CFG


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
    ring_id = int(
        input('Свободный ring_id (если это первое erps кольцо на l3, то введите 1)> '))
    match ring_params[2]:
        case 'hw':
            print(f'\n{cmd.hw_l3(ring_params, ring_id)}\n')
        case 'snr':
            print(f'\n{cmd.snr_l3(ring_params, ring_id)}\n')
        case 'dgs':
            print(f'\n{cmd.d_link_l3(ring_params, ring_id)}\n')
        case 'ex':
            print(f'\n{cmd.ex_l3(ring_params, ring_id)}\n')


def wait_for_confirmation():
    while input() != '':
        time.sleep(1)


def print_switch_status(ring, swi):
    print(f"{len(ring) - ring.index(swi)} - {swi['model']} {swi['l2_sw_ip']} {swi['ports']} is OK")


def configure_switches(ring, raps_vlan, remove):
    for swi in ring:
        if remove:
            CFG(raps_vlan, swi, True).remove()
        else:
            if swi.get('owner'):
                print(f"{swi['l2_sw_ip']} - owner configuration...")
                CFG(raps_vlan, swi, False).owner()
            else:
                CFG(raps_vlan, swi, False).common()
        print_switch_status(ring, swi)
        time.sleep(3)


def handle_adding_erps(ring, raps_vlan, ring_params, ring_id):
    print_l3_config(ring_params)
    print('\033[33mЕсли настройки верны, скопируйте конфиг на l3 и нажмите Enter для продолжения настройки кольца!\033[0m')
    wait_for_confirmation()
    configure_switches(ring, raps_vlan, False)
    print(f'Ring {ring_id} - ERPS ON!')


def handle_removal_erps(ring, raps_vlan, ring_id):
    print('\033[33mУбедитесь, что кольцо работает со стороны "жёлтого" коммутатора! Если всё правильно нажмите Enter.\033[0m')
    wait_for_confirmation()
    configure_switches(ring, raps_vlan, True)
    print(f'Ring {ring_id} - ERPS REMOVE!')


def mutation(ring_id, rm=False):
    ring_params, ring = Parse(*ini(), ring_id).get_data()

    if not all(len(p['ports']) == 2 for p in ring) or len(ring) == 1:
        print("\033[31mRing NOT OK! Правильно ли обозначены rudiment'ы и uplink'и на схеме?\033[0m")
        return
    print(f'Ring is OK! {len(ring)} коммутаторов.')

    raps_vlan = ring_params[1] if ring_params[1] else input('Введите raps_vlan> ')

    if not rm:
        handle_adding_erps(ring, raps_vlan, ring_params, ring_id)
    else:
        handle_removal_erps(ring, raps_vlan, ring_id)


if __name__ == "__main__":
    import sys
    from argparse import ArgumentParser

    def Parser():
        parser = ArgumentParser(
            prog='mutation',
            add_help=False,
            description='''ERPS ring mutation.''',
            epilog='''\033[36m(ノ ˘_˘)ノ\033[0m
                    https://github.com/dammaer/'''
        )
        parser.add_argument('-h', '--help', action='help')
        parser.add_argument('-id', '--ring_id',
                            help=('Указать id кольца'),
                            metavar='\b')
        parser.add_argument('-rm', '--remove_erps',
                            action='store_true',
                            help='Удалить ERPS с кольца')
        return parser

    prs = Parser().parse_args(sys.argv[1:])
    mutation(prs.ring_id, prs.remove_erps) if prs.ring_id else print(
        'Запуск с указанием ring-id. Пример: python mutation.py -id 100')

import pexpect
import subprocess
import socket
import time
import commands as cmd

from configparser import ConfigParser

config = ConfigParser()
config.read('settings.ini')

LOCAL_DIR = config.get('tftp', 'local_dir')
TFTP_IP = config.get('tftp', 'tftp_ip')
TFTP_PATCH = config.get('tftp', 'tftp_patch')

MODELS = {'S29': 'SNR', 'S29U': 'SNR', 'S29P': 'SNR', 'S52U': 'SNR_S52',
          'TP34U': 'TP_Link',
          'D3528': 'D_Link', 'D3000': 'D_Link', 'D3120': 'D_Link', 'G3000': 'D_Link',
          'Q28': 'QTECH'}

OWNER_MODELS = {'S29': 'SNR_owner', 'S29U': 'SNR_owner', 'S29P': 'SNR_owner',
                'TP34U': 'TP_Link_owner'}

TPLINK_RM_PATTERNS = ['erps ring 1', 'description "ring 1"', 'control-vlan',
                      'protected-instance 1', 'raps-mel 3', 'version 2']


def download_from_tftp(swi_ip):
    try:
        command = f"tftp {TFTP_IP} -c get {TFTP_PATCH + swi_ip} {LOCAL_DIR + swi_ip}"
        subprocess.run(command, shell=True, check=True)
        print(f"Config '{swi_ip}' downloaded successfully in local dir.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to download file from TFTP server: {e}")


def upload_to_tftp(swi_ip):
    try:
        command = f"tftp {TFTP_IP} -c put {LOCAL_DIR + swi_ip} {TFTP_PATCH + swi_ip}"
        subprocess.run(command, shell=True, check=True)
        print(f"Config '{swi_ip}' uploaded successfully in TFTP dir.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to upload file to TFTP server: {e}")


def config_change(patterns, swi_ip):
    with open(LOCAL_DIR + swi_ip, 'r') as f:
        cfg = f.readlines()

    print('Config change...')
    new_cfg = []
    for v in cfg:
        if not any(v.lstrip().startswith(pattern) for pattern in patterns):
            new_cfg.append(v)

    with open(LOCAL_DIR + swi_ip, 'w') as f:
        f.write(''.join(new_cfg))


def is_alive(host):
    try:
        with socket.create_connection((host, 23), 2):
            return True
    except OSError:
        return False


class CFG():
    EXCEPT = [pexpect.TIMEOUT, pexpect.EOF]

    def __init__(self, raps_vlan, swi, rm):
        self.raps_vlan = raps_vlan
        self.swi_ip = swi['l2_sw_ip']
        self.model = swi['model']
        self.user = swi['auth'][0]
        self.passw = swi['auth'][1]
        self.ports = swi['ports']
        self.rm = rm
        self.telnet = pexpect.spawn(f"telnet {self.swi_ip}", timeout=10,
                                    encoding="utf-8")

    def SNR(self):
        prompt = ["#", "[Y/N]"]
        self.telnet.expect("login")
        self.telnet.sendline(self.user)
        self.telnet.expect("[Pp]assword")
        self.telnet.sendline(self.passw)
        self.telnet.expect(prompt)
        self.telnet.sendline("terminal length 0")
        self.telnet.expect(prompt)
        for c in cmd.snr(self.raps_vlan, self.ports, self.rm):
            self.telnet.sendline(c)
            self.telnet.expect(prompt, timeout=None)
        self.telnet.close()

    def SNR_owner(self):
        prompt = ["#", "[Y/N]"]
        self.telnet.expect("login")
        self.telnet.sendline(self.user)
        self.telnet.expect("[Pp]assword")
        self.telnet.sendline(self.passw)
        self.telnet.expect(prompt)
        self.telnet.sendline("terminal length 0")
        self.telnet.expect(prompt)
        for c in cmd.snr_owner(self.raps_vlan, self.ports):
            self.telnet.sendline(c)
            self.telnet.expect(prompt, timeout=None)
        self.telnet.close()

    def SNR_S52(self):
        prompt = [">", "#", "[Y/N]"]
        self.telnet.expect("login")
        self.telnet.sendline(self.user)
        self.telnet.expect("[Pp]assword")
        self.telnet.sendline(self.passw)
        self.telnet.expect(prompt, timeout=None)
        self.telnet.sendline("enable")
        self.telnet.expect(prompt)
        self.telnet.sendline("terminal length 0")
        self.telnet.expect(prompt)
        for c in cmd.snr_s52(self.raps_vlan, self.ports, self.rm):
            self.telnet.sendline(c)
            self.telnet.expect(prompt, timeout=None)
        self.telnet.close()

    def D_Link(self):
        prompt = ["#"]
        self.telnet.expect("[Uu]ser[Nn]ame")
        self.telnet.sendline(self.user)
        self.telnet.expect("[Pp]ass[Ww]ord")
        self.telnet.sendline(self.passw)
        self.telnet.expect(prompt)
        for c in cmd.d_link(self.raps_vlan, self.ports, self.rm):
            self.telnet.sendline(c)
            self.telnet.expect(prompt, timeout=None)
        self.telnet.close()

    def TP_Link(self):
        prompt = ['>', '#', ':']
        self.telnet.expect(prompt)
        self.telnet.sendline(f'{self.user}\r\n')
        self.telnet.expect(prompt)
        self.telnet.sendline(f'{self.passw}\r\n')
        self.telnet.expect(prompt)
        self.telnet.sendline('enable\r\n')
        self.telnet.expect(prompt)
        if not self.rm:
            for c in cmd.tp_link(self.raps_vlan, self.ports):
                self.telnet.sendline(f'{c}\r\n')
                self.telnet.expect(prompt, timeout=None)
            self.telnet.close()
        else:
            print(f'{self.model} {self.swi_ip} (yebanyy tp-link) configuration...')
            self.telnet.sendline('copy startup-config tftp ip-address '
                                 f'{TFTP_IP} filename {TFTP_PATCH + self.swi_ip}\r\n')
            self.telnet.expect(prompt)
            download_from_tftp(self.swi_ip)
            config_change(TPLINK_RM_PATTERNS, self.swi_ip)
            upload_to_tftp(self.swi_ip)
            self.telnet.sendline('copy tftp startup-config ip-address '
                                 f'{TFTP_IP} filename {TFTP_PATCH + self.swi_ip}\r\n')
            self.telnet.expect('(Y/N)')
            self.telnet.sendline('y\r\n')
            self.telnet.expect('...')
            self.telnet.close()
            print('Switch rebooting (~ 3 min)...')
            time.sleep(5)  # берем паузу чтобы коммутатор точно не был доступен
            while not is_alive(self.swi_ip):
                time.sleep(1)
            print('Switch is alive!')

    def TP_Link_owner(self):
        prompt = ['>', '#', ':']
        self.telnet.expect(prompt)
        self.telnet.sendline(f'{self.user}\r\n')
        self.telnet.expect(prompt)
        self.telnet.sendline(f'{self.passw}\r\n')
        self.telnet.expect(prompt)
        self.telnet.sendline('enable\r\n')
        self.telnet.expect(prompt)
        for c in cmd.tp_link_owner(self.raps_vlan, self.ports):
            self.telnet.sendline(f'{c}\r\n')
            self.telnet.expect(prompt, timeout=None)
        self.telnet.close()

    def QTECH(self):
        prompt = ["#", "[Y/N]"]
        self.telnet.expect("login")
        self.telnet.sendline(self.user)
        self.telnet.expect("[Pp]assword")
        self.telnet.sendline(self.passw)
        self.telnet.expect(prompt)
        self.telnet.sendline("terminal length 0")
        self.telnet.expect(prompt)
        for c in cmd.qtech(self.raps_vlan, self.ports):
            self.telnet.sendline(c)
            self.telnet.expect(prompt, timeout=None)
        self.telnet.close()

    def common(self):
        method = getattr(self, MODELS[self.model])
        method()

    def owner(self):
        method = getattr(self, OWNER_MODELS[self.model])
        method()

    remove = common


if __name__ == "__main__":
    # CFG('30',
    #     {'l2_sw_ip': '10.59.100.22', 'uplink': False, 'model': 'TP34U',
    #      'ports': ['26', '25'], 'auth': ['root', 'root'],
    #      'owner': False}, rm=True).remove()
    pass

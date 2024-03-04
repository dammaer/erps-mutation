import pexpect

import commands as cmd

MODELS = {'S29': 'SNR', 'S29U': 'SNR',
          'TP34U': 'TP_Link',
          'D3528': 'D_Link', 'D3000': 'D_Link', 'D3120': 'D_Link', 'G3000': 'D_Link'}

OWNER_MODELS = {'S29': 'SNR_owner', 'S29U': 'SNR_owner',
                'TP34U': 'TP_Link_owner'}


class CFG():
    EXCEPT = [pexpect.TIMEOUT, pexpect.EOF]

    def __init__(self, raps_vlan, swi):
        self.raps_vlan = raps_vlan
        self.model = swi['model']
        self.user = swi['auth'][0]
        self.passw = swi['auth'][1]
        self.ports = swi['ports']
        self.telnet = pexpect.spawn(f"telnet {swi['l2_sw_ip']}", timeout=10,
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
        for c in cmd.snr(self.raps_vlan, self.ports):
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

    def D_Link(self):
        prompt = ["#"]
        self.telnet.expect("[Uu]ser[Nn]ame")
        self.telnet.sendline(self.user)
        self.telnet.expect("[Pp]ass[Ww]ord")
        self.telnet.sendline(self.passw)
        self.telnet.expect(prompt)
        for c in cmd.d_link(self.raps_vlan, self.ports):
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
        for c in cmd.tp_link(self.raps_vlan, self.ports):
            self.telnet.sendline(f'{c}\r\n')
            self.telnet.expect(prompt, timeout=None)
        self.telnet.close()

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

    def common(self):
        method = getattr(self, MODELS[self.model])
        method()

    def owner(self):
        method = getattr(self, OWNER_MODELS[self.model])
        method()


if __name__ == "__main__":
    # CFG('10.59.100.3', 'passwd', 'TP34U', 30, [25, 26]).copy()
    pass

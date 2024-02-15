import pexpect

from commands import d_link, snr, snr_owner, tp_link


class CFG():
    EXCEPT = [pexpect.TIMEOUT, pexpect.EOF]
    MODELS = {'S29': 'SNR', 'S29U': 'SNR',
              'TP34U': 'TP_Link',
              'D3528': 'D_Link', 'D3000': 'D_Link'}

    def __init__(self, l2_sw_ip, auth, model, raps_vlan, ports):
        self.model = model
        self.user = auth[0]
        self.passw = auth[1]
        self.raps_vlan = raps_vlan
        self.ports = ports
        self.telnet = pexpect.spawn(f"telnet {l2_sw_ip}", timeout=10,
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
        for c in snr(self.raps_vlan, self.ports):
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
        for c in snr_owner(self.ports):
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
        for c in d_link(self.raps_vlan, self.ports):
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
        for c in tp_link(self.raps_vlan, self.ports):
            self.telnet.sendline(f'{c}\r\n')
            self.telnet.expect(prompt, timeout=None)
        self.telnet.close()

    def copy(self):
        method = getattr(self, self.MODELS[self.model])
        method()


if __name__ == "__main__":
    # CFG('10.59.100.3', 'passwd', 'TP34U', 30, [25, 26]).copy()
    pass
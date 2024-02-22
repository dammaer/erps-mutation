import re
import bs4
import requests


class Parse():
    def __init__(self, adm_urls, login, passw, ring_id):
        self.adm_urls = adm_urls
        svg_url = f'{adm_urls[0]}{ring_id}'
        self.ring_id = ring_id
        self.cookies = {'ko-login': login, 'ko-passw': passw}
        self.swi_auth = self.get_auth()
        self.svg_table = self.get_table(svg_url, {"class": "datatable"})
        self.lines = self.svg_table.find_all("line")
        self.first_swi_x = 0
        self.first_swi_y = 0
        self.ring_direction = []

    def get_table(self, url, attr):
        html_page = requests.get(url, cookies=self.cookies).text
        soup = bs4.BeautifulSoup(html_page, 'lxml')
        table = soup.find('table', attrs=attr)
        return table

    def get_auth(self):
        auth_url = f'{self.adm_urls[1]}{self.ring_id}'
        table = self.get_table(
            auth_url, {"id": "swtable"}).find_all("td", attrs={"class": "switch"})
        swi_auth = {}
        for swi in table:
            swi_auth |= {swi["switch"]: [swi["login"], swi["password"]]}
        return swi_auth

    def get_ring_params(self):
        ring_params_url = f'{self.adm_urls[2]}{self.ring_id}'
        table = self.get_table(ring_params_url, {"id": "ring_edit"})
        name = re.sub(r'.ERPS[.\w+]|.ERPS', '',  table.find_all("input", attrs={"id": "description"})[0]['value'], flags=re.I)
        raps_vlan = table.find_all("input", attrs={"id": "stp"})[0]['value']
        l3_ports1 = table.find_all("input", attrs={"id": "port1"})[0]['value'].split(':')[1]
        l3_ports2 = table.find_all("input", attrs={"id": "port2"})[0]['value'].split(':')[1]
        return name, raps_vlan, (l3_ports1, l3_ports2)

    def get_first_swi(self):
        for row in self.svg_table.find_all("g"):
            if "yellow" in str(row.contents[0]["style"]):
                data = {'l2_sw_ip': row['l2_sw_ip']}
                ports = []
                self.first_swi_x = int(row.contents[0]["x"])
                self.first_swi_y = int(row.contents[0]["y"])
                for r in list(row):
                    if int(r["y"]) == self.first_swi_y + 58:
                        data |= {'model': r.contents[0]}
                    if int(r["y"]) == self.first_swi_y + 4:
                        ports.append(r.contents[0])
                    if r.get('fill') == 'red':
                        ports.append(r.contents[0].split(' ')[0])
                data |= {'ports': ports,
                         'auth': self.swi_auth[row['l2_sw_ip']]}
                return data

    def filter_ports(self, swi_x, swi_y, bottom_port):
        next_line = {}
        for line in self.lines:
            if int(line["x2"]) == swi_x + 100 and int(line["y2"]) == swi_y + 60:
                if self.find_swi(int(line["x1"]) - 100,  int(line["y1"])).get('uplink'):
                    next_line |= {int(line["x1"]): True}
                elif self.find_swi(int(line["x1"]) - 100,  int(line["y1"])).get('rudiment'):
                    next_line |= {int(line["x1"]): False}
                else:
                    next_line |= {int(line["x1"]): any(int(l["x2"]) == int(line["x1"]) and int(
                        l["y2"]) == int(line["y1"]) + 60 for l in self.lines)}
        filter_ports = []
        for i, v in enumerate(sorted(next_line.items())):
            if v[1] is True:
                filter_ports.append(bottom_port[i])
        return filter_ports

    def find_swi(self, x, y):
        for row in self.svg_table.find_all("g"):
            if int(row.contents[0]["x"]) == x and int(row.contents[0]["y"]) == y:
                data = {'l2_sw_ip': row['l2_sw_ip']}
                uplink = False
                owner = True if "palegreen" in str(
                    row.contents[0]["style"]) else False
                ports = []
                if 'rudiment' in row.get_text().lower():
                    data |= {'rudiment': True}
                    return data
                if 'uplink' in row.get_text().lower():
                    uplink = True
                    bottom_port = re.findall(
                        r'(uplink)(\d+)', re.sub(r'\s+|-', '', row.get_text().lower()))
                    ports.append(bottom_port[0][1])
                    data |= {'uplink': uplink}
                for r in list(row):
                    if int(r["y"]) == y + 58:
                        data |= {'model': r.contents[0]}
                    if int(r["y"]) == y + 4:
                        ports.append(r.contents[0])
                    if int(r["y"]) == y + 63 and uplink is False:
                        bottom_port = r.contents[0].split(' ')
                        if len(bottom_port) > 1:
                            bottom_port = self.filter_ports(x, y, bottom_port)
                        ports.extend(bottom_port)
                data |= {'ports': ports, 'auth': self.swi_auth[row['l2_sw_ip']],
                         'owner': owner}
                return data

    def find_direction(self):
        swi_x, swi_y = self.first_swi_x, self.first_swi_y
        top_swi, end_ring = False, False
        switches = []
        while not end_ring:
            for line in self.lines:
                # от первого свича вверх
                if not top_swi and ((int(line["x1"]) == swi_x + 100 and int(line["y1"]) == swi_y)):
                    swi_x, swi_y = int(line["x2"]) - 100, int(line["y2"]) - 60
                    switches.append(self.find_swi(swi_x, swi_y))
                    top_swi = True if swi_y == 5 else False
                elif top_swi and (int(line["x2"]) == swi_x + 100 and int(line["y2"]) == swi_y + 60):
                    line_x1, line_y1 = int(line["x1"]) - 100, int(line["y1"])
                    swi_data = self.find_swi(line_x1, line_y1)
                    if swi_data.get('uplink'):
                        switches.append(swi_data)
                        end_ring = True
                    elif any(int(l["x2"]) == line_x1 + 100 and int(l["y2"]) == line_y1 + 60 for l in self.lines):
                        # Проверяем, что после коммутатора есть соединение со следующим комутатором
                        if not swi_data.get('rudiment'):
                            swi_x, swi_y = line_x1, line_y1
                            switches.append(swi_data)
        return switches

    def get_data(self):
        data = [self.get_first_swi()]
        data.extend(self.find_direction())
        ring_params = self.get_ring_params()
        return ring_params, data


if __name__ == "__main__":
    pass

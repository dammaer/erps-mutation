def tp_link(raps_vlan, ports):
    port0, port1 = ports
    config = ['conf',
              f'no vlan {raps_vlan}',
              'spanning-tree',
              'spanning-tree mode mstp',
              'spanning-tree mst configuration',
              'instance 1 vlan 2-4094',
              '#',
              'erps ring 1',
              f'control-vlan {raps_vlan}',
              'protected-instance 1',
              'wtr-timer 5',
              'guard-timer 200',
              'holdoff-timer 50',
              'raps-mel 3',
              'version 2',
              '#',
              f'int ten-gigabitEthernet 1/0/{port0}',
              'erps ring 1',
              f'int ten-gigabitEthernet 1/0/{port1}',
              'erps ring 1',
              '#',
              'exit',
              'copy running-config startup-config'
              ]
    return config


def tp_link_owner(raps_vlan, ports):
    port0, port1 = ports
    config = ['conf',
              f'no vlan {raps_vlan}',
              'spanning-tree',
              'spanning-tree mode mstp',
              'spanning-tree mst configuration',
              'instance 1 vlan 2-4094',
              '#',
              'erps ring 1',
              f'control-vlan {raps_vlan}',
              'protected-instance 1',
              'wtr-timer 5',
              'guard-timer 200',
              'holdoff-timer 50',
              'raps-mel 3',
              'version 2',
              '#',
              f'int ten-gigabitEthernet 1/0/{port0}',
              'erps ring 1',
              f'int ten-gigabitEthernet 1/0/{port1}',
              'erps ring 1 rpl owner',
              '#',
              'exit',
              'copy running-config startup-config'
              ]
    return config


def snr(raps_vlan, ports):
    port0, port1 = ports
    config = ['conf',
              f'vlan {raps_vlan}',
              '!',
              'spanning-tree mst configuration',
              'instance 1 vlan 2-4094',
              '!',
              'erps-ring 1',
              'erps-instance 1',
              f'control-vlan {raps_vlan}',
              'wtr-timer 5',
              'guard-timer 200',
              'holdoff-timer 5',
              'raps-mel 3',
              'protected-instance 1',
              '!',
              '!',
              f'int ethernet 1/0/{port0}',
              f'swi trunk allowed vlan add {raps_vlan}',
              'erps-ring 1 port0',
              f'int ethernet 1/0/{port1}',
              f'swi trunk allowed vlan add {raps_vlan}',
              'erps-ring 1 port1',
              '!',
              'exit',
              'write',
              'y'
              ]
    return config


def snr_owner(raps_vlan, ports):
    port0, port1 = ports
    config = ['conf',
              f'vlan {raps_vlan}',
              '!',
              'spanning-tree mst configuration',
              'instance 1 vlan 2-4094',
              '!',
              'erps-ring 1',
              'erps-instance 1',
              'rpl port1 owner',
              f'control-vlan {raps_vlan}',
              'wtr-timer 5',
              'guard-timer 200',
              'holdoff-timer 5',
              'raps-mel 3',
              'protected-instance 1',
              '!',
              '!',
              f'int ethernet 1/0/{port0}',
              f'swi trunk allowed vlan add {raps_vlan}',
              'erps-ring 1 port0',
              f'int ethernet 1/0/{port1}',
              f'swi trunk allowed vlan add {raps_vlan}',
              'erps-ring 1 port1',
              '!',
              'exit',
              'write',
              'y'
              ]
    return config


def snr_s52(raps_vlan, ports):
    port0, port1 = ports
    pmap = {'25': 'xe1', '26': 'xe2',
            '27': 'xe3', '28': 'xe4'}
    config = ['configure',
              f'vlan {raps_vlan}',
              'spanning-tree mst configuration',
              'instance 1 vlan 2-4094',
              'exit',
              'erps-ring 1',
              'erps-instance 1',
              f'control-vlan {raps_vlan}',
              'wtr-timer 5',
              'guard-timer 200',
              'holdoff-timer 5',
              'raps-mel 3',
              'protected-instance 1',
              'exit',
              'exit',
              f'interface {pmap[port0]}',
              f'swi trunk allowed vlan add {raps_vlan}',
              'erps-ring 1 port0',
              f'interface {pmap[port1]}',
              f'swi trunk allowed vlan add {raps_vlan}',
              'erps-ring 1 port1',
              'exit',
              'exit',
              'write',
              ]
    return config


def d_link(raps_vlan, ports):
    port0, port1 = ports
    config = [f'create vlan vlan{raps_vlan} tag {raps_vlan}',
              f'config vlan vlan{raps_vlan} add tagged {port0},{port1}',
              'enable erps',
              f'create erps raps_vlan {raps_vlan}',
              f'config erps raps_vlan {raps_vlan} timer holdoff_time 5000 guard_time 2000 wtr_time 5',
              f'config erps raps_vlan {raps_vlan} rpl_port none',
              f'config erps raps_vlan {raps_vlan} rpl_owner disable',
              f'config erps raps_vlan {raps_vlan} ring_mel 3',
              f'config erps raps_vlan {raps_vlan} ring_port west {port0}',
              f'config erps raps_vlan {raps_vlan} ring_port east {port1}',
              f'config erps raps_vlan {raps_vlan} protected_vlan add vlanid 2-{int(raps_vlan) - 1},{int(raps_vlan) + 1}-4094',
              'config erps log enable',
              f'config erps raps_vlan {raps_vlan} state enable',
              'save']
    return config


def qtech(raps_vlan, ports):
    port0, port1 = ports
    config = ['conf',
              f'vlan {raps_vlan}',
              '!',
              'spanning-tree mst configuration',
              'instance 1 vlan 2-4094',
              '!',
              'erps-ring 1',
              'erps-instance 1',
              f'control-vlan {raps_vlan}',
              'wtr-timer 5',
              'guard-timer 200',
              'holdoff-timer 5',
              'raps-mel 3',
              'protected-instance 1',
              '!',
              '!',
              f'int ethernet 1/{port0}',
              f'swi trunk allowed vlan add {raps_vlan}',
              'erps-ring 1 port0',
              f'int ethernet 1/{port1}',
              f'swi trunk allowed vlan add {raps_vlan}',
              'erps-ring 1 port1',
              '!',
              'exit',
              'write',
              'y'
              ]
    return config


def hw_l3(ring_params, ring_id):
    descr, raps_vlan, _, ports = ring_params
    config = ['system-view',
              'stp region-configuration',
              'instance 1 vlan 2 to 3999',
              'active region-configuration',
              'q',
              f'erps ring {ring_id}',
              f'description {descr}',
              f'control-vlan {raps_vlan}',
              'protected-instance 1',
              'holdoff-timer 50',
              'raps-mel 3',
              'version v2',
              'q',
              f'interface XGigabitEthernet 0/0/{ports[0]}',
              'stp disable',
              f'erps ring {ring_id}',
              'q',
              f'interface XGigabitEthernet 0/0/{ports[1]}',
              'stp disable',
              f'erps ring {ring_id}',
              'q'
              ]
    if ring_id != 1:
        del config[1:5]
    return '\n'.join(config)


def snr_l3(ring_params, ring_id):
    descr, raps_vlan, _, ports = ring_params
    config = ['conf',
              f'vlan {raps_vlan}',
              '!',
              'spanning-tree mst configuration',
              'instance 1 vlan 2-4094',
              'exit',
              f'erps-ring {ring_id}',
              'erps-instance 1',
              f'description {descr}',
              f'control-vlan {raps_vlan}',
              'wtr-timer 5',
              'guard-timer 200',
              'holdoff-timer 5',
              'raps-mel 3',
              'protected-instance 1',
              '!',
              '!',
              f'int ethernet 1/0/{ports[0]}',
              f'erps-ring {ring_id} port0',
              'no loopback-detection specified-vlan 1-4094',
              f'swi trunk allowed vlan add {raps_vlan}',
              f'int ethernet 1/0/{ports[1]}',
              f'erps-ring {ring_id} port1',
              'no loopback-detection specified-vlan 1-4094',
              f'swi trunk allowed vlan add {raps_vlan}',
              '!',
              'exit',
              'write',
              'y']
    if ring_id != 1:
        del config[3:6]
    return '\n'.join(config)


def d_link_l3(ring_params, ring_id):
    _, raps_vlan, _, ports = ring_params
    config = [f'create vlan vlan{raps_vlan} tag {raps_vlan}',
              f'config vlan vlan{raps_vlan} add tagged {ports[0]},{ports[1]}',
              'enable erps',
              f'create erps raps_vlan {raps_vlan}',
              f'config erps raps_vlan {raps_vlan} timer holdoff_time 5000 guard_time 2000 wtr_time 5',
              f'config erps raps_vlan {raps_vlan} rpl_port none',
              f'config erps raps_vlan {raps_vlan} rpl_owner disable',
              f'config erps raps_vlan {raps_vlan} ring_mel 3',
              f'config erps raps_vlan {raps_vlan} ring_port west {ports[0]}',
              f'config erps raps_vlan {raps_vlan} ring_port east {ports[1]}',
              f'config erps raps_vlan {raps_vlan} protected_vlan add vlanid 2-{int(raps_vlan) - 1},{int(raps_vlan) + 1}-4094',
              'config erps log enable',
              f'config loopdetect ports {ports[0]},{ports[1]} state disable',
              f'config erps raps_vlan {raps_vlan} state enable',
              'save']
    if ring_id != 1:
        del config[2:3]
    return '\n'.join(config)


def ex_l3(ring_params, ring_id):
    descr, raps_vlan, _, ports = ring_params
    config = ['enable erps',
              f'create vlan vlan{raps_vlan}',
              f'configure vlan vlan{raps_vlan} tag {raps_vlan}',
              f'configure vlan vlan{raps_vlan} add ports {ports[0]},{ports[1]} tagged',
              f'create erps {descr}',
              f'configure erps {descr} add control vlan vlan{raps_vlan}',
              f'configure erps {descr} ring-port east {ports[0]}',
              f'configure erps {descr} ring-port west {ports[1]}',
              f'configure erps {descr} timer hold-off 5000',
              f'configure erps {descr} timer guard 2000',
              f'enable erps {descr}']
    if ring_id != 1:
        del config[0:1]
    return '\n'.join(config)

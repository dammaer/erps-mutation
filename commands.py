def tp_link(raps_vlan, ports):
    port0, port1 = ports
    config = ['configure',
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


def snr(raps_vlan, ports):
    port0, port1 = ports
    config = ['configure',
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
              'erps-ring 1 port0',
              f'int ethernet 1/0/{port1}',
              'erps-ring 1 port1',
              '!',
              'exit',
              'write',
              'y'
              ]
    return config


def snr_owner(raps_vlan, ports):
    port0, port1 = ports
    config = ['configure',
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
              'erps-ring 1 port0',
              f'int ethernet 1/0/{port1}',
              'erps-ring 1 port1',
              '!',
              'exit',
              'write',
              'y'
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

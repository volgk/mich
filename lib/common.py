# This file is part of mich program.
# See LICENSE file for copyright and license details.

import os
import random
import re
import sys
from subprocess import CalledProcessError, PIPE, Popen, run

import lib.iputils

filename = '/tmp/saved_route'


def route_table_save(filename):
    "Save the current routing table."
    f = open(filename, 'wb')
    run(['ip', 'route', 'save'], stdout=f)
    f.close()


def route_table_restore(filename):
    "Restore the routing table."
    f = open(filename, 'rb')
    run(['ip', 'route', 'restore'], stdin=f)
    f.close()


def file_remove(filename):
    "Remove the file."
    os.remove(filename)


def file_replace_data(filename, old, new):
    "Swap old file data to new."
    f = open(filename, 'rb+')
    data = f.read()
    f.seek(0)
    f.write(data.replace(old, new))
    f.close()


def ip2bytes(ip):
    "Turns a string into bytes."
    return bytes([int(x) for x in ip.split('.')])


def am_I_root():
    "Check for root privileges."
    if os.geteuid() != 0:
        return False
    return True


def get_active_hosts():
    "Get all actives MACs and IP addresses from the local network."
    with Popen(['arp-scan', '-l', '-r', '5'], stdout=PIPE) as proc:
        data = proc.stdout.read().decode('utf-8')
        ip_list = re.findall(
                    '(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})\\s', data)
        mac_list = re.findall(
                    '\\s+((?:[0-9A-Fa-f]{2}:){5}(?:[0-9A-Fa-f]){2})\\s+', data)
        return ip_list, mac_list


def get_random_mac():
    "Create a random MAC."
    gen_hex = lambda length: ''.join(random.choice('0123456789abcdef')
                                     for _ in range(length))
    gen_mac = ':'.join(gen_hex(2) for _ in range(6))
    return gen_mac


def get_random_ip(ipmask):
    "Create a random IP depending on the mask."
    ip, mask = ipmask.split('/')
    if mask == '24':
        ip = ip.split('.')[0:3]
        ip = '.'.join(ip + [str(random.randint(2, 255))])
    elif mask == '16':
        ip = ip.split('.')[0:2]
        ip = '.'.join(ip + [str(random.randint(2, 255)) for _ in range(2)])
    elif mask == '8':
        ip = ip.split('.')[0:1]
        ip = '.'.join(ip + [str(random.randint(2, 255)) for _ in range(3)])
    else:
        print('Error. Input the correct mask: 24, 16 or 8.', file=sys.stderr)
        return None
    return ip


def get_broadcast(ipmask):
    "Get the broadcast address to set MAC depending on the mask."
    ip, mask = ipmask.split('/')
    if mask == '24':
        ip = ip.split('.')[0:3]
        ip = '.'.join(ip + ['255'])
    elif mask == '16':
        ip = ip.split('.')[0:2]
        ip = '.'.join(ip + ['255']*2)
    elif mask == '8':
        ip = ip.split('.')[0:1]
        ip = '.'.join(ip + ['255']*3)
    else:
        print('Error. Input the correct mask: 24, 16 or 8.', file=sys.stderr)
        return None
    return ip


def set_custom_mac(iface, mac):
    "Set custom MAC address."
    try:
        lib.iputils.set_iface_down(iface)

        try:
            lib.iputils.set_iface_mac(iface, mac)
        except AttributeError:
            pass

    except CalledProcessError:
        print(f"Can't set this MAC: {mac}\n"
              f"Choose another or set a custom one.",
              file=sys.stderr)

    finally:
        lib.iputils.set_iface_up(iface)


def set_random_mac(iface, mac):
    "Set random MAC address."
    try:
        lib.iputils.set_iface_down(iface)
        lib.iputils.run_set_address(iface, get_random_mac())
        lib.iputils.set_iface_up(iface)
    except CalledProcessError:
        set_random_mac(iface, mac)


def set_mac(iface, mac):
    "Set the new MAC address."
    current_mac = lib.iputils.get_current_mac(iface)
    active_hosts_mac = get_active_hosts()[1]
    restricted_macs = ['0', '00:00:00:00:00:00', current_mac] + active_hosts_mac

    route_table_save(filename)
    if mac != '0':
        set_custom_mac(iface, mac)
    elif mac == '0':
        set_random_mac(iface, mac)
        if mac in restricted_macs:
            set_random_mac(iface, mac)
    route_table_restore(filename)
    file_remove(filename)


def set_ip(iface, ipmask):
    "Set new IP address."
    if not re.match('^\\d{,3}\\.\\d{,3}\\.\\d{,3}\\.\\d{,3}(?:/\\d{,2})?$',
                    ipmask):
        print(f"Wrong IP address: {ipmask}", file=sys.stderr)
        return

    if '/' in ipmask:
        new_ip = get_random_ip(ipmask)
        if new_ip is None:
            return
        brd_ip = get_broadcast(ipmask)
    else:
        new_ip = ipmask
        brd_ip = lib.iputils.get_current_broadcast(iface)

    old_ip = lib.iputils.get_current_ip(iface)
    route_table_save(filename)
    lib.iputils.ip_addr_flush(iface)
    lib.iputils.ip_addr_add(iface, new_ip, brd_ip)
    lib.iputils.ip_route_flush()
    file_replace_data(filename, ip2bytes(old_ip), ip2bytes(new_ip))
    route_table_restore(filename)
    file_remove(filename)

# End of file

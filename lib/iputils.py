# This file is part of mich_program.
# See LICENSE file for copyright and license details.

import re
from subprocess import PIPE, Popen, run, STDOUT

import lib.common


def get_current_ifaces():
    "Show actives interfaces."
    with Popen(['ip', 'link', 'show'], stdout=PIPE) as proc:
        return re.findall('\\d+:\\s([0-9a-z]+):',
                          proc.stdout.read().decode('utf-8'))


def get_current_ip(iface):
    "Show the current IP address on interface."
    with Popen(['ip', 'addr', 'show', 'dev', iface], stdout=PIPE) as proc:
        ip = re.search('inet ((\\d{1,3}\\.){3}\\d{1,3})/',
                       proc.stdout.read().decode('utf-8'))
        return ip.group(1) if ip else 'IP not found.'


def get_current_mac(iface):
    "Show the current MAC address on interface."
    with Popen(['ip', 'link', 'show', 'dev', iface], stdout=PIPE) as proc:
        mac = re.search('ether\\s(([0-9a-f]{2}:){5}[0-9a-f]{2})\\sbrd',
                        proc.stdout.read().decode('utf-8'))
        return mac.group(1) if mac else 'MAC address not found'


def run_set_address(iface, mac):
    "Set MAC on interface."
    try:
        mac = lib.common.get_random_mac()
        run(['ip', 'link', 'set', 'dev', iface, 'address', mac],
            check=True, stdout=PIPE, stderr=STDOUT)
    except AttributeError:
        pass


def get_current_broadcast(iface):
    "Get the current broadcast for set MAC."
    with Popen(['ip', 'addr', 'show', 'dev', iface], stdout=PIPE) as proc:
        broadcast = re.search('brd ((\\d{1,3}\\.){3}\\d{1,3}) scope',
                              proc.stdout.read().decode('utf-8'))
        return broadcast.group(1) if broadcast else\
            'broadcast address not found'


def set_iface_down(iface):
    "Set interface down."
    run(['ip', 'link', 'set', 'dev', iface, 'down'], check=True)


def set_iface_mac(iface, mac):
    "Set MAC address on interface."
    run(['ip', 'link', 'set', 'dev', iface, 'address', mac],
        check=True, stdout=PIPE, stderr=STDOUT)


def set_iface_up(iface):
    "Set interface up."
    run(['ip', 'link', 'set', 'dev', iface, 'up'], check=True)


def ip_addr_flush(iface):
    "Flush the interface."
    run(['ip', 'addr', 'flush', iface])


def ip_addr_add(iface, ip, brd):
    "Add the new IP address."
    run(['ip', 'addr', 'add', ip, 'brd', brd, 'dev', iface])


def ip_route_flush():
    "Flush all interfaces."
    run(['ip', 'route', 'flush', 'all'])

# End of file

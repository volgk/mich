% mich(1) Mich User Manual
% Stamatin Cristina <dear.volgk@gmail.com>
% January 6, 2019

# NAME

mich - MAC/IP changer

# SYNOPSIS

mich [*-h*] [*-i [IFACE]*] [*-a [IPMASK]*] [*-m [MAC]*]

# DESCRIPTION

Mich is a program for manipulating MAC and IP addresses. It's written for *Linux* and uses *iputils* for that. Also, it uses arp-scan to resolve conflicts due to setting IP/MAC addresses which exists in the local network.

Mich can get the current interfaces/IP/MAC and set like specified IP/MAC to the interface, and a random one.

See EXAMPLES for more usage info.

# OPTIONS

-i [IFACE]
:   Without an argument, displays a list of interfaces. If the argument *IFACE* is specified, all further steps to set the IP/MAC addresses will be performed on this interface.

-a [IPMASK]
:   For this option the interface must be specified: `-i IFACE`. Without an argument, displays the current IP address on the specified interface. If the argument is an IP (192.168.0.7), then this IP will be set. If the argument is a MASK (192.168.0.0/24), then will be set a random IP in the corresponding range. 

-m [MAC]
:   For this option the interface must be specified: `-i IFACE`. Without an argument, displays the current MAC address on the specified interface. If the argument is 0, then will be set a random MAC.

Before setting of IP and MAC addresses, mich checks if the chosen IP/MAC is unique in the LAN (via *arp-scan*). 

For setting IP/MAC addresses the program must be run with root privileges. Try sudo or run in root shell.

# EXAMPLES

Get the list of network interfaces

    $ mich -i
    ['lo', 'enp1s0f1', 'wlp2s0']
    
Get current IP address

    $ mich -i wlp2s0 -a
    192.168.0.102
    
Get current MAC address

    $ mich -i wlp2s0 -m
    00:11:22:33:44:55:66

Save current IP and MAC to file

    $ mich -i wlp2s0 -a -m > /tmp/ipmac

Set IP address

    $ sudo mich -i wlp2s0 -a 192.168.0.105
    
Set random IP address

    $ sudo mich -i wlp2s0 -a 192.168.0.0/24
    Will set an IP from range: 192.168.0.[1-254]
    
Set random IP and MAC addresses every minute

    $ sudo watch -n 60 ./mich -i wlp2s0 -a 192.168.0.0/24 -m 0

Set MAC address

    $ sudo mich -i wlp2s0 -m XX:XX:XX:XX:XX:XX

Set random MAC address

    $ sudo mich -i wlp2s0 -m 0

Restore previous IP and MAC from saved file

    $ sudo mich -i wlp2s0 -a $(head -1 /tmp/ipmac) \
      -m $(tail -1 /tmp/ipmac)
        
# LICENSE

GPLv3

# LINKS

https://github.com/volgk/mich

# SEE ALSO

ip(8), arp-scan(1)

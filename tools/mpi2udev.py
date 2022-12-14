#!/usr/bin/env python3
# Generate udev rules from music player identification (.mpi) files
#
# (C) 2009 Canonical Ltd.
# Author: Martin Pitt <martin.pitt@ubuntu.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys, configparser, os.path, os

# translation of mpi Device keys to udev attributes
mpi2udev = {
    'vendorid': 'ATTRS{idVendor}=="%s"',
    'productid': 'ATTRS{idProduct}=="%s"',
    'usbvendor': 'ATTRS{vendor}=="%s"',
    'usbmodel': 'ATTRS{model}=="%s"',
    'usbproduct': 'ATTRS{product}=="%s"',
    'usbmanufacturer': 'ATTRS{manufacturer}=="%s"',
}

def parse_mpi(mpi):
    '''Print udev rule for given ConfigParser object.'''

    cp = configparser.RawConfigParser()
    assert cp.read(mpi, encoding='UTF-8')

    rule = ''

    for name in ['usbvendor', 'usbproduct', 'usbmodel', 'usbmanufacturer']:
        try:
            value = cp.get('Device', name)
            rule += mpi2udev[name] % value + ', '
        except configparser.NoOptionError:
            continue


    # if no info other than idVendor+idProduct was found, we don't need to write an udev rule
    if not rule:
        return

    try:
        usbids = {}
        for usbid in cp.get('Device', 'devicematch').split(';'):
            if len(usbid.split(':')) != 3:
                continue
            (subsystem, vid, pid) = usbid.split(':')
            if subsystem != "usb":
                continue
            if vid in usbids:
                usbids[vid].append(pid)
            else:
                usbids[vid] = [ pid ]

        for vid, pids in usbids.items():
            rule += 'ATTRS{idVendor}=="%s", ATTRS{idProduct}=="%s"'% (vid, '|'.join(pids)) + ', '
    except configparser.NoOptionError:
        pass

    # if no information was found, don't write a rule at all
    if not rule:
        return

    try:
        m = cp.get('Device', 'product')
        rule = ('# %s\n' % m) + rule
    except configparser.NoOptionError:
        pass

    rule += 'ENV{ID_MEDIA_PLAYER}="%s"' % os.path.splitext(os.path.basename(mpi))[0]

    # do we have an icon?
    try:
        icon = cp.get('Device', 'icon')
        # breaks media player detection : https://bugs.launchpad.net/ubuntu/+source/gvfs/+bug/657609
        # rule += ', ENV{UDISKS_PRESENTATION_ICON_NAME}="%s"' % icon
    except configparser.NoOptionError:
        pass

    # empty line between blocks
    rule += '\n\n'

    # write bytes so that we are independent of the locale
    os.write(sys.stdout.fileno(), rule.encode('UTF-8'))

#
# main
#

# udev rules header
os.write(sys.stdout.fileno(), b'''ACTION!="add|change", GOTO="media_player_end"
# catch MTP devices
ENV{DEVTYPE}=="usb_device", GOTO="media_player_start"

# catch UMS devices
SUBSYSTEM!="block", GOTO="media_player_end"
SUBSYSTEMS=="usb", GOTO="media_player_start"
GOTO="media_player_end"

LABEL="media_player_start"

''')

# parse MPI files
for f in sys.argv[1:]:
    parse_mpi(f)

# udev rules footer
os.write(sys.stdout.fileno(), b'\nLABEL="media_player_end"\n')

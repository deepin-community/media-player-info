#!/usr/bin/env python3
# Generate hwdb file from music player identification (.mpi) files
#
# (C) 2009 Canonical Ltd.
# (C) 2013 Tom Gundersen <teg@jklm.no>
# Author: Tom Gundersen <teg@jklm.no>
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

def parse_mpi(mpi):
    '''Print hwdb file for given ConfigParser object.'''

    cp = configparser.RawConfigParser()
    assert cp.read(mpi, encoding='UTF-8')

    # if we have more info than just idVendor+idProduct we need to use an udev rule,
    # so don't write an hwdb entry
    for name in ['usbvendor', 'usbproduct', 'usbmodel', 'usbmanufacturer']:
        try:
            cp.get('Device', name)
            return
        except configparser.NoOptionError:
            continue

    block = ''

    try:
        m = cp.get('Device', 'product')
        block += '# ' + m + '\n'
    except configparser.NoOptionError:
        pass

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
            for pid in pids:
                block += 'usb:v%sp%s*\n' % (vid.upper(), pid.upper())
                block += ' ID_MEDIA_PLAYER=%s\n' % os.path.splitext(os.path.basename(mpi))[0]

                # do we have an icon?
                try:
                    icon = cp.get('Device', 'icon')
                    block += ' ID_MEDIA_PLAYER_ICON_NAME=%s\n' % icon
                    # breaks media player detection : https://bugs.launchpad.net/ubuntu/+source/gvfs/+bug/657609
                    #block += ' UDISKS_PRESENTATION_ICON_NAME=%s\n' % icon
                except configparser.NoOptionError:
                    # icon defaults to phone icon these days, so set it explicitly
                    block += ' ID_MEDIA_PLAYER_ICON_NAME=multimedia-player\n'
                    pass

                # empty line between blocks
                block += '\n'

                # write bytes so that we are independent of the locale
                os.write(sys.stdout.fileno(), block.encode('UTF-8'))

    except configparser.NoOptionError:
        pass

#
# main
#

# parse MPI files
for f in sys.argv[1:]:
    parse_mpi(f)

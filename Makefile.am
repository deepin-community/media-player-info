DISTCHECK_CONFIGURE_FLAGS = --with-udevdir='$${libdir}/udev-distcheck'

mpidir = $(datadir)/media-player-info
dist_mpi_DATA =  $(shell find $(top_srcdir)/media-players -name "*.mpi" -printf "%p\n" | LC_ALL=C sort)

udevrulesdir = $(UDEV_DIR)/rules.d
nodist_udevrules_DATA = 40-usb-media-players.rules

40-usb-media-players.rules: $(dist_mpi_DATA) $(top_srcdir)/tools/mpi2udev.py
	$(PYTHON) $(top_srcdir)/tools/mpi2udev.py $(dist_mpi_DATA) > 40-usb-media-players.rules
	$(PYTHON) $(top_srcdir)/tools/udev-syntax-check.py 40-usb-media-players.rules

udevhwdbdir = $(UDEV_DIR)/hwdb.d
nodist_udevhwdb_DATA = 20-usb-media-players.hwdb

20-usb-media-players.hwdb: $(dist_mpi_DATA) $(top_srcdir)/tools/mpi2hwdb.py
	$(PYTHON) $(top_srcdir)/tools/mpi2hwdb.py $(dist_mpi_DATA) > 20-usb-media-players.hwdb

clean-local:
	rm -f 40-usb-media-players.rules 20-usb-media-players.hwdb

EXTRA_DIST = \
	tools/COPYING \
	tools/mpi2udev.py \
	tools/mpi2hwdb.py \
	tools/udev-syntax-check.py

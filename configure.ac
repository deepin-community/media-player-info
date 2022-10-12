AC_INIT(media-player-info, 24, devkit-devel@lists.freedesktop.org)
AM_INIT_AUTOMAKE([foreign])
AC_CONFIG_SRCDIR([media-players/])

# require hwdb support
PKG_CHECK_MODULES(UDEV, udev >= 196)

AC_ARG_WITH(udevdir,
	    AS_HELP_STRING([--with-udevdir=DIR],[Installation path for udev rules @<:@auto@:>@]),
	    [ac_with_udevdir=$withval],
	    [ac_with_udevdir=""])
if test "${ac_with_udevdir}" = ""; then
	ac_with_udevdir=`$PKG_CONFIG --variable=udevdir udev`
fi

AM_PATH_PYTHON([3])

AC_MSG_NOTICE([installing udev rules in ${ac_with_udevdir}/rules.d])
AC_SUBST([UDEV_DIR],[${ac_with_udevdir}])

AC_CONFIG_FILES([Makefile])
AC_OUTPUT

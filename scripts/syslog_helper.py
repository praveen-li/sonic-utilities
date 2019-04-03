#!/usr/bin/env python

#################################################################################
# This is a syslog Helper file							#
# All plugins use this script to use regular syslog file			#
#################################################################################

try:
    import exceptions
    import sys
    import syslog
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")


# ========================== Syslog wrappers ==========================

class LogHelper(object):

	def __init__(self, id):
		self.SYSLOG_IDENTIFIER = id

	def log_info(self, msg, also_print_to_console=False):
		syslog.openlog(self.SYSLOG_IDENTIFIER)
		syslog.syslog(syslog.LOG_INFO, msg)
		syslog.closelog()

		if also_print_to_console:
			print(msg)

	def log_warning(self, msg, also_print_to_console=False):
		syslog.openlog(self.SYSLOG_IDENTIFIER)
		syslog.syslog(syslog.LOG_WARNING, msg)
		syslog.closelog()

		if also_print_to_console:
			print(msg)

	def log_error(self, msg, also_print_to_console=False):
		syslog.openlog(self.SYSLOG_IDENTIFIER)
		syslog.syslog(syslog.LOG_ERR, msg)
		syslog.closelog()

		if also_print_to_console:
			print(msg)


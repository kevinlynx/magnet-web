#!/bin/env python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/magnet/app")

from app import app as application
application.startup('/var/www/magnet/app/app_online.cfg', False, '/var/www/magnet/app/black_list.txt')


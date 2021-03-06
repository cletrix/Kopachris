# -*- coding: utf-8 -*-

## Begin license block ##

##           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
##                   Version 2, December 2004
##
## Copyright (C) 2013 Christopher Koch <kopachris@gmail.com>
##
## Everyone is permitted to copy and distribute verbatim or modified
## copies of this license document, and changing it is allowed as long
## as the name is changed.
##
##           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
##  TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
##
##  0. You just DO WHAT THE FUCK YOU WANT TO.

## End license block ##

from datetime import datetime
from bot_utils import store_dict

db.define_table('event_log',
                Field('event_time', 'datetime', default=datetime.today()),
                Field('event_type', 'string'),
                Field('event_source', 'string'),
                Field('event_target', 'string'),
                Field('event_message', 'string'),
                Field('event_hostmask', 'string'),
                )

db.define_table('bot_modules',
                Field('mod_enabled', 'boolean', default=True),
                Field('event_type', 'string', default='PRIVMSG'),  # event this module handles
                Field('name', 'string', unique=True, length=64, writable=False),  # module name, will be used by __import__()
                Field('description', 'string'),  # display description
                Field('chans_en', 'list:string'),  # channels module is enabled on unless nicks_dis
                Field('chans_dis', 'list:string'),  # channels module is always disabled on
                Field('nicks_en', 'list:string'),  # nicks module is enabled by
                Field('nicks_dis', 'list:string'),  # nicks module is always disabled by
                Field('vars_pre', 'string', unique=True, length=8),
                )

vars_tbl = db.define_table('bot_vars',
                           Field('tbl_k', 'string', length=32),
                           Field('v', 'string', length=512),
                           )

## default variables for bot_vars
bot_vars = {'nick': 'BotenAlfred',
            'user': 'BotenAlfred',
            'rname': 'BotenAlfred',
            'server': 'irc.esper.net',
            'port': 6666,
            'chans': '#HotelReddit,',
            'pid': 0,  # Python instance that the bot runs in
            'ppid': 0,  # Parent of ^, sh instance created by os.system()
            'apache_pid': 0,  # Apache thread, parent of initial fork(), must kill to clean up zombies
            #'default': 1,  # used to test
            }
default = db(db.bot_vars.tbl_k == 'pid').select()
if not len(default):
    # store defaults
    store_dict(bot_vars, db)

## store db for modules to access
#from gluon import current
#from gluon.storage import Storage
#current.bot = Storage()
#current.bot.db = db

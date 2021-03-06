#!/usr/bin/env python
# coding: utf8
#from gluon import *
from gluon.tools import Auth
from gluon.storage import Storage
import bot_utils
import urllib2

## Description stored in db.bot_modules
description = "!py - evaluate a python expression"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "py_"

## Event type handled by this module
event_type = "PRIVMSG"

trusted_users = {'Kopachris': 'codk4819071993'}

def init(db):
    pass


def remove(db):
    pass


def run(bot, event, db):
    mod_name = __name__.rsplit('.', 1)[1]
    this_mod = db(db.bot_modules.name == mod_name).select()
    prefix = this_mod.first().vars_pre
    s = event.message.split()
    try:
        trusted = bot.trusted
    except AttributeError:
        trusted = set()

    auth = Auth(db)
    auth.define_tables(username=False, signature=False)

    if event.message.lower().startswith('!ident') and len(s) == 2:
        bot.bot_reply(event, "!ident is deprecated.  Please use !auth.")
        return
        if event.source in trusted_users:
            if s[1] == trusted_users[event.source]:
                trusted.add(event.source)
                bot.trusted = trusted
                bot.bot_reply(event, "Thank you.")
            else:
                bot.bot_reply(event, "Authorization denied.")
        else:
            bot.bot_reply(event, "Authorization denied.")

    if event.message.lower().startswith('!auth') and len(s) > 2:
        user = auth.login_bare(s[1], ' '.join(s[2:]))
        if user and auth.has_membership(user_id=user.id, role='wheel'):
            trusted.add(event.source)
            bot.trusted = trusted
            bot.bot_reply(event, "Thank you.")
        else:
            bot.bot_reply(event, "Authorization denied.")

    if event.message.lower().startswith('!pyc') and len(s) > 1:
        if event.source in trusted:
            import os, sys
            sys.stdout = open('stdout.tmp', 'w')
            exec ' '.join(s[1:])
            sys.stdout.flush()
            sys.stdout = sys.__stdout__
            o = open('stdout.tmp', 'r')
            for line in o.readlines():
                bot.bot_reply(event, line, False)
            o.close()
        else:
            bot.bot_reply(event, "Please authorize yourself with !auth")
    elif event.message.lower().startswith('!py') and len(s) > 1:
        if event.source in trusted:
            import os, sys, sh
            res = str(eval(' '.join(s[1:])))
            #import re
            #res = re.sub(r'[^\w\d\s]', '', res)
            bot.bot_reply(event, res.strip('\n'))
        else:
            bot.bot_reply(event, "Please authorize yourself with !auth")
            
    if s[0] == '!enmod' and len(s) > 1:
        if event.source in trusted:
            mods = s[1:]
            mods_tbl = db.bot_modules
            for m in mods:
                db(mods_tbl.name == m).update(mod_enabled=True)
            bot.bot_reply(event, 'Module(s) {} enabled'.format(', '.join(mods)))
        else:
            bot.bot_reply(event, "Please authenticate yourself with !auth")
    if s[0] == '!dismod' and len(s) > 1:
        if event.source in trusted:
            mods = s[1:]
            mods_tbl = db.bot_modules
            for m in mods:
                db(mods_tbl.name == m).update(mod_enabled=False)
            bot.bot_reply(event, 'Module(s) {} disabled'.format(', '.join(mods)))
        else:
            bot.bot_reply(event, "Please authenticate yourself with !auth")
    if s[0] == '!say' and len(s) > 1:
        if event.source in trusted:
            bot.bot_reply(event, ' '.join(s[1:]), False)
    if (s[0] == '!msg' or s[0] == '!sayc') and len(s) > 2:
        if event.source in trusted:
            target = s[1]
            msg = ' '.join(s[2:])
            bot.bot_log('PRIVMSG', bot.nickname, target, msg)
            bot.send_message(target, msg)
    if s[0] == '!me' and len(s) > 2:
        if event.source in trusted:
            target = s[1]
            msg = ' '.join(s[2:])
            bot.bot_log('CTCP_ACTION', bot.nickname, target, msg)
            bot.send_action(target, msg)
    if s[0] == '!join' and len(s) > 1:
        if event.source in trusted:
            for chan in s[1:]:
                bot.join(chan)
        else:
            bot.bot_reply(event, "Please authenticate yourself with !auth")
    if s[0] == '!part' and len(s) > 1:
        if event.source in trusted:
            for chan in s[1:]:
                bot.part(chan)
        else:
            bot.bot_reply(event, "Please authenticate yourself with !auth")
    if s[0] == '!traceback':
        if event.source in trusted:
            tb = db(db.event_log.event_type == 'ERROR').select().last()
            msg = tb.event_message.split('\n')
            bot.bot_reply(event, 'Time: {}, Source: {}, Target: {}'.format(tb.event_time, tb.event_source, tb.event_target))
            for line in msg:
                bot.bot_reply(event, line, False)
    if s[0] == '!log':
        return
        if event.source in trusted:
            event.target = bot.nickname  # so replies will automatically go to private message
            temp = "{} {}: {} <{}> {}"  # time, target, type, source, message
            if len(s) > 1:
                numlogs = int(s[1])
            else:
                numlogs = 20
            logs = db().select(db.event_log.ALL, orderby=~db.event_log.id, limitby=(0,numlogs)).as_list(storage_to_dict=False)[-1::-1]
            for l in logs:
                msg = temp.format(l.event_time, l.event_target, l.event_type, l.event_source, l.event_message)
                bot.bot_reply(event, msg)
        elif event.target.startswith('#'):
            chan = event.target
            event.target = bot.nickname  # so replies will go to private message
            temp = "{} {}: {} <{}> {}"  # time, target, type, source, message
            if len(s) > 1:
                numlogs = min(int(s[1]), 50)
            else:
                numlogs = 20
            logs = db(db.event_log.event_target == chan).select(db.event_log.ALL, orderby=~db.event_log.id, limitby=(0,numlogs)).as_list(storage_to_dict=False)[-1::-1]
            for l in logs:
                msg = temp.format(l.event_time, l.event_target, l.event_type, l.event_source, l.event_message)
                bot.bot_reply(event, msg)
        else:
            bot.bot_reply(event, "Please authenticate yourself with !auth")
    if s[0] == '!nick' and len(s) == 2:
        if event.source in trusted:
            bot.set_nickname(s[1])
        else:
            bot.bot_reply(event, "Please authenticate yourself with !auth")

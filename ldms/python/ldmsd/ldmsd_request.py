#######################################################################
# -*- c-basic-offset: 8 -*-
# Copyright (c) 2016-2018 National Technology & Engineering Solutions
# of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with
# NTESS, the U.S. Government retains certain rights in this software.
# Copyright (c) 2016-2018 Open Grid Computing, Inc. All rights reserved.
#
# This software is available to you under a choice of one of two
# licenses.  You may choose to be licensed under the terms of the GNU
# General Public License (GPL) Version 2, available from the file
# COPYING in the main directory of this source tree, or the BSD-type
# license below:
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#      Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#      Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#      Neither the name of Sandia nor the names of any contributors may
#      be used to endorse or promote products derived from this software
#      without specific prior written permission.
#
#      Neither the name of Open Grid Computing nor the names of any
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
#
#      Modified source versions must be plainly marked as such, and
#      must not be misrepresented as being the original software.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#######################################################################
import struct
import cmd
import json
import argparse
import sys
import traceback
import re
import errno

class LDMSDRequestException(Exception):
    '''Raise when there is an error in the ldmsd request module'''
    def __init__(self, message, errcode, *args):
        self.message = message
        self.errcode = errcode
        super(LDMSDRequestException, self).__init__(message, errcode, *args)

class LDMSD_Req_Attr(object):
    LDMSD_REQ_ATTR_SZ = 12
    LDMSD_REQ_ATTR_DISCRIM_SZ = 4

    NAME = 1
    INTERVAL = 2
    OFFSET = 3
    REGEX = 4
    TYPE = 5
    PRODUCER = 6
    INSTANCE = 7
    XPRT = 8
    HOST = 9
    PORT = 10
    MATCH = 11
    PLUGIN = 12
    CONTAINER = 13
    SCHEMA = 14
    METRIC = 15
    STRING = 16
    UDATA = 17
    BASE = 18
    INCREMENT = 19
    LEVEL = 20
    PATH = 21
    TIME = 22
    PUSH = 23
    TEST = 24
    REC_LEN = 25
    JSON = 26
    PERM = 27
    AUTO_SWITCH = 28
    PEER_NAME = 29
    TIMEOUT_FACTOR = 30
    AUTO_INTERVAL = 31
    UID = 32
    GID = 33
    STREAM = 34
    COMP_ID = 35
    QUERY = 36
    AUTH = 37
    ENV = 38
    CMDLINE = 39
    CFGCMD = 40
    LAST = 41

    NAME_ID_MAP = {'name': NAME,
                   'component_id':COMP_ID,
                   'interval': INTERVAL,
                   'interval_us': INTERVAL,
                   'offset': OFFSET,
                   'regex': REGEX,
                   'type': TYPE,
                   'producer': PRODUCER,
                   'instance': INSTANCE,
                   'xprt': XPRT,
                   'host': HOST,
                   'port': PORT,
                   'match': MATCH,
                   'plugin': PLUGIN,
                   'container': CONTAINER,
                   'schema': SCHEMA,
                   'string': STRING,
                   'metric': METRIC,
                   'udata': UDATA,
                   'base': BASE,
                   'incr': INCREMENT,
                   'level': LEVEL,
                   'path': PATH,
                   'time': TIME,
                   'push': PUSH,
                   'test': TEST,
                   "REC_LEN": REC_LEN,
                   "json": JSON,
                   'perm': PERM,
                   'auto_switch': AUTO_SWITCH,
                   'peer_name': PEER_NAME,
                   'timeout_factor': TIMEOUT_FACTOR,
                   'auto_interval': AUTO_INTERVAL,
                   'uid': UID,
                   'gid': GID,
                   'stream': STREAM,
                   'query': QUERY,
                   'auth': AUTH,
                   'cmdline': CMDLINE,
                   'cfgcmd': CFGCMD,
                   'env': ENV,
                   'envvar': ENV,
                   'TERMINATING': LAST
        }

    def __init__(self, value = None, attr_name = None, attr_id = None, attr_len = None):
        self.discrim = 1
        if attr_id:
            if attr_id not in self.NAME_ID_MAP.values():
                raise LDMSDRequestException("The attr_id '%d' is not valid" % attr_id, errno.EINVAL)
            self.attr_id = attr_id
            self.attr_name = self.NAME_ID_MAP.keys()[self.NAME_ID_MAP.values().index(self.attr_id)]
        else:
            if attr_name:
                try:
                    self.attr_id = self.NAME_ID_MAP[attr_name]
                except KeyError:
                    raise
                self.attr_name = attr_name
            else:
                # this is the last attribute.
                self.attr_id = self.LAST

        if self.attr_id == self.LAST:
            # terminating attribute
            self.packed = struct.pack("!L", 0)
            self.attr_len = 4
            self.discrim = 0
        else:
            self.attr_value = value
            if value is None:
                self.attr_len = 0
                self.fmt = '!LLL'
                self.packed = struct.pack(self.fmt, 1, self.attr_id,
                                                    self.attr_len)
            else:
                # One is added to account for the terminating zero
                if attr_len is None:
                    self.attr_len = int(len(value)+1)
                else:
                    self.attr_len = attr_len

                self.fmt = '!LLL'
                if (self.attr_id == self.REC_LEN):
                    self.fmt += 'L'
                else:
                    self.fmt += str(self.attr_len) + 's'
                self.packed = struct.pack(self.fmt, 1, self.attr_id,
                                          self.attr_len, self.attr_value)

    def __len__(self):
        return len(self.packed)

    def __repr__(self):
        if self.discrim:
            return "<LDMSD_Req_Attr discrim=%s attr_id=%d attr_len=%d attr_value=%s>" % (
                    self.discrim, self.attr_id, self.attr_len, self.attr_value)
        else:
            return "<LDMSD_Req_Attr discrim=0>"

    @classmethod
    def getDiscrimSize(cls):
        return cls.LDMSD_REQ_ATTR_DISCRIM_SZ

    @classmethod
    def unpack(cls, buf):
        (discrim, ) = struct.unpack('!L', buf[:4])
        if discrim == 0:
            return LDMSD_Req_Attr(attr_id = cls.LAST)

        (discrim, attr_id, attr_len, ) = struct.unpack('!LLL',
                                            buf[:cls.LDMSD_REQ_ATTR_SZ])

        if attr_id == cls.REC_LEN:
            fmt = '!L'
        else:
            fmt = str(attr_len) + 's'

        (attr_value,) = struct.unpack(fmt, buf[cls.LDMSD_REQ_ATTR_SZ:attr_len + cls.LDMSD_REQ_ATTR_SZ])
        if attr_id != cls.REC_LEN:
            attr_value = attr_value.strip('\0')

        attr = LDMSD_Req_Attr(value = attr_value, attr_id = attr_id, attr_len = attr_len)
        return attr

    def pack(self):
        return self.packed

class LDMSD_Request(object):
    EXAMPLE = 1
    GREETING = 2

    PRDCR_ADD = 0x100
    PRDCR_DEL = 0x100 + 1
    PRDCR_START = 0x100 + 2
    PRDCR_STOP = 0x100 + 3
    PRDCR_STATUS = 0x100 + 4
    PRDCR_START_REGEX = 0x100 + 5
    PRDCR_STOP_REGEX = 0x100 + 6
    PRDCR_SET_STATUS = 0x100 + 7
    PRDCR_SUBSCRIBE = 0x100 + 8

    STRGP_ADD = 0x200
    STRGP_DEL = 0x200 + 1
    STRGP_START = 0x200 + 2
    STRGP_STOP = 0x200 + 3
    STRGP_STATUS = 0x200 + 4
    STRGP_PRDCR_ADD = 0X200 + 5
    STRGP_PRDCR_DEL = 0X200 + 6
    STRGP_METRIC_ADD = 0X200 + 7
    STRGP_METRIC_DEL = 0X200 + 8

    UPDTR_ADD = 0X300
    UPDTR_DEL = 0X300 + 1
    UPDTR_START = 0X300 + 2
    UPDTR_STOP = 0X300 + 3
    UPDTR_STATUS = 0x300 + 4
    UPDTR_PRDCR_ADD = 0X300 + 5
    UPDTR_PRDCR_DEL = 0X300 + 6
    UPDTR_MATCH_ADD = 0X300 + 7
    UPDTR_MATCH_DEL = 0X300 + 8

    SMPLR_ADD = 0X400
    SMPLR_DEL = 0X400 + 1
    SMPLR_START = 0X400 + 2
    SMPLR_STOP = 0X400 + 3
    SMPLR_STATUS = 0X400 + 4

    PLUGN_ADD = 0X500
    PLUGN_DEL = 0X500 + 1
    PLUGN_STATUS = 0x500 + 2
    PLUGN_LOAD = 0X500 + 3
    PLUGN_TERM = 0X500 + 4
    PLUGN_CONFIG = 0X500 + 5
    PLUGN_LIST = 0x500 + 6
    PLUGN_SETS = 0x500 + 7
    PLUGN_USAGE = 0x500 + 8
    PLUGN_QUERY = 0x500 + 9

    SET_UDATA = 0x600
    SET_UDATA_REGEX = 0x600 + 1
    VERBOSITY_CHANGE = 0x600 + 2
    DAEMON_STATUS = 0x600 + 3
    VERSION = 0x600 + 4
    ENV = 0x600 + 5
    INCLUDE = 0x600 + 6
    ONESHOT = 0x600 + 7
    LOGROTATE = 0x600 + 8
    EXIT_DAEMON = 0x600 + 9
    SET_ROUTE = 0X600 + 11
    EXPORT_CONFIG = 0x600 + 12

    FAILOVER_CONFIG        = 0x700
    FAILOVER_PEERCFG_START = 0x700  +  1
    FAILOVER_PEERCFG_STOP  = 0x700  +  2
    FAILOVER_MOD           = 0x700  +  3
    FAILOVER_STATUS        = 0x700  +  4

    FAILOVER_START        =  0x770
    FAILOVER_STOP         =  0x770 + 1

    SETGROUP_ADD = 0x800
    SETGROUP_MOD = 0x800 + 1
    SETGROUP_DEL = 0x800 + 2
    SETGROUP_INS = 0x800 + 3
    SETGROUP_RM  = 0x800 + 4

    STREAM_PUBLISH = 0x900
    STREAM_SUBSCRIBE = STREAM_PUBLISH + 1

    LDMSD_REQ_ID_MAP = {
            'example': {'id': EXAMPLE},
            'greeting': {'id': GREETING},

            'smplr_add': {'id': SMPLR_ADD},
            'smplr_del': {'id': SMPLR_DEL},
            'smplr_start': {'id': SMPLR_START},
            'smplr_stop': {'id': SMPLR_STOP},
            'smplr_status': {'id': SMPLR_STATUS},

            'prdcr_add': {'id': PRDCR_ADD},
            'prdcr_del': {'id': PRDCR_DEL},
            'prdcr_start': {'id': PRDCR_START},
            'prdcr_stop': {'id': PRDCR_STOP},
            'prdcr_status': {'id': PRDCR_STATUS},
            'prdcr_start': {'id': PRDCR_START},
            'prdcr_start_regex': {'id': PRDCR_START_REGEX},
            'prdcr_stop': {'id': PRDCR_STOP},
            'prdcr_stop_regex': {'id': PRDCR_STOP_REGEX},
            'prdcr_set_status': {'id': PRDCR_SET_STATUS},
            'prdcr_subscribe': {'id': PRDCR_SUBSCRIBE},

            'strgp_add': {'id': STRGP_ADD},
            'strgp_del': {'id': STRGP_DEL},
            'strgp_start': {'id': STRGP_START},
            'strgp_stop': {'id': STRGP_STOP},
            'strgp_status': {'id': STRGP_STATUS},
            'strgp_prdcr_add': {'id': STRGP_PRDCR_ADD},
            'strgp_prdcr_del': {'id': STRGP_PRDCR_DEL},
            'strgp_metric_add': {'id': STRGP_METRIC_ADD},
            'strgp_metric_del': {'id': STRGP_METRIC_DEL},

            'updtr_add': {'id': UPDTR_ADD},
            'updtr_del': {'id': UPDTR_DEL},
            'updtr_start': {'id': UPDTR_START},
            'updtr_stop': {'id': UPDTR_STOP},
            'updtr_status': {'id': UPDTR_STATUS},
            'updtr_prdcr_add': {'id': UPDTR_PRDCR_ADD},
            'updtr_prdcr_del': {'id': UPDTR_PRDCR_DEL},
            'updtr_match_add': {'id': UPDTR_MATCH_ADD},
            'updtr_match_del': {'id': UPDTR_MATCH_DEL},

            'plugn_status': {'id': PLUGN_STATUS},
            'load': {'id': PLUGN_LOAD},
            'term': {'id': PLUGN_TERM},
            'config': {'id': PLUGN_CONFIG},
            'usage': {'id': PLUGN_USAGE},
            'list': {'id': PLUGN_LIST},

            'plugn_sets': {'id': PLUGN_SETS},
            'plugn_query': {'id': PLUGN_QUERY},

            'udata': {'id': SET_UDATA},
            'udata_regex': {'id': SET_UDATA_REGEX},
            'loglevel': {'id': VERBOSITY_CHANGE},
            'daemon_status': {'id': DAEMON_STATUS},
            'version': {'id': VERSION},
            'env': {'id': ENV},
            'include': {'id': INCLUDE},
            'oneshot': {'id': ONESHOT},
            'logrotate': {'id': LOGROTATE},
            'daemon_exit': {'id': EXIT_DAEMON},
            'failover_config'        : {'id' : FAILOVER_CONFIG},
            'failover_peercfg_start' : {'id' : FAILOVER_PEERCFG_START},
            'failover_peercfg_stop'  : {'id' : FAILOVER_PEERCFG_STOP},
            'failover_status'        : {'id' : FAILOVER_STATUS},
            'failover_start'         : {'id' : FAILOVER_START},
            'failover_stop'          : {'id' : FAILOVER_STOP},
            'set_route': {'id': SET_ROUTE},

            'setgroup_add'  :  {'id':  SETGROUP_ADD},
            'setgroup_mod'  :  {'id':  SETGROUP_MOD},
            'setgroup_del'  :  {'id':  SETGROUP_DEL},
            'setgroup_ins'  :  {'id':  SETGROUP_INS},
            'setgroup_rm'   :  {'id':  SETGROUP_RM},

            'publish'       :  {'id': STREAM_PUBLISH },
            'subscribe'     :  {'id' : STREAM_SUBSCRIBE },

            'export' :  {'id':  EXPORT_CONFIG},
        }

    TYPE_CONFIG_CMD = 1
    TYPE_CONFIG_RESP = 2
    TYPE_LAST = 3

    MARKER = 0xffffffff

    SOM_FLAG = 1
    EOM_FLAG = 2
    message_number = 1
    header_size = 24
    def __init__(self, command=None, command_id=None, message=None, attrs=None):
        if command_id is None and command is None:
            raise Exception("Need either command or command_id")
        if command_id is None:
            if command not in self.LDMSD_REQ_ID_MAP.keys():
                raise KeyError("Command '{0}' is not supported.".format(command))
            command_id = self.LDMSD_REQ_ID_MAP[command]['id']
        self.command_id = command_id
        self.attrs = attrs
        self.message = message
        self.request_size = self.header_size
        self.message_number = LDMSD_Request.message_number

        if message:
            self.request_size += len(self.message)

        # store all packed attribute value pairs
        self.packed_attrs = ""  # excluding the terminating attribute
        self.packed_attrs_sz = 0 # excluding the terminating attribute
        # Compute the extra size occupied by the attributes and add it
        # to the request size in the request header

        # Aggregate the attributes
        if attrs:
            for attr in attrs:
                self.packed_attrs += attr.pack()

        self.request_size += len(self.packed_attrs)
        # Account for size of terminating 0
        self.request_size += LDMSD_Req_Attr.getDiscrimSize()

        self.request = struct.pack('!LLLLLL', self.MARKER, self.TYPE_CONFIG_CMD,
                                   LDMSD_Request.SOM_FLAG | LDMSD_Request.EOM_FLAG,
                                   self.message_number, command_id, self.request_size)

        # Add any message payload
        if message:
            self.request += message

        self.request += self.packed_attrs
        self.request += struct.pack('!L', 0) # terminate list

        self.response = {'errcode': None, 'msg': None}
        LDMSD_Request.message_number += 1

    def _newRecord(self, flags, offset, sz):
        """Create a record

        offset is offset after the request header
        sz is the size after the offset
        """
        rec_len = self.header_size + sz
        if flags & LDMSD_Request.EOM_FLAG:
            rec_len += LDMSD_Req_Attr.getDiscrimSize()
        hdr = struct.pack('!LLLLLL', self.MARKER, self.TYPE_CONFIG_CMD, flags,
                                   self.message_number, self.command_id, rec_len)
        rec = hdr + self.packed_attrs[offset:offset+sz]
        if flags & LDMSD_Request.EOM_FLAG:
            rec += struct.pack('!L', 0) # adding the terminating attribute
        return rec

    def __repr__(self):
        s = "<LDMSD_Request message_number=%d command_id=%d request_size=%d" % (
                self.message_number, self.command_id, self.request_size)
        if (self.attrs is None) or (len(self.attrs) == 0):
            s += "attrs=[]>"
        else:
            for attr in self.attrs:
                s += "\n    %s" % repr(attr)
            s += "\n]>"
        return s

    def message_number_get(self):
        return self.message_number

    def send(self, ctrl):
        data_len = self.request_size - self.header_size - LDMSD_Req_Attr.getDiscrimSize()
        max_msg = ctrl.getMaxRecvLen()
        offset = 0
        try:
            while True:
                remaining = max_msg - self.header_size - LDMSD_Req_Attr.getDiscrimSize()
                if remaining >= data_len:
                    remaining = data_len
                if offset == 0:
                    flags = LDMSD_Request.SOM_FLAG
                else:
                    flags = 0
                if data_len == remaining:
                    flags |= LDMSD_Request.EOM_FLAG
                rec = self._newRecord(flags, offset, remaining)
                if len(rec) > max_msg:
                    raise RuntimeError("Record size exceeds the maximum of transport message length")
                offset += remaining
                data_len -= remaining
                ctrl.send_command(bytes(rec))
                if data_len == 0:
                    break
        except:
            raise

    def receive(self, ctrl):
        self.response = None
        resp = None
        while True:
            record = ctrl.receive_response()
            if record is None:
                raise LDMSDRequestException(message="No data received", errcode=errno.ECONNRESET)
            (marker, msg_type, msg_flags, msg_no,
             errcode, rec_len) = struct.unpack('!LLLLLL',
                                               record[:self.header_size])

            if marker != self.MARKER:
                raise ValueError("Record is missing the marker")
            data = record[self.header_size:]
            if resp is None:
                resp = data
            else:
                resp += data
            if (msg_flags & LDMSD_Request.EOM_FLAG) != 0:
                break

        attr_list = []

        if resp is not None:
            offset = 0
            while True:
                attr = LDMSD_Req_Attr.unpack(resp[offset:])
                if attr.discrim == 0:
                    break
                if attr.attr_id == attr.REC_LEN:
                    raise LDMSDRequestException(message="The request is too big.",
                                                  errcode=errcode)
                attr_list.append(attr)
                offset += attr.LDMSD_REQ_ATTR_SZ + attr.attr_len

        msg = None
        if len(attr_list) == 1:
            if (attr_list[0].attr_id == LDMSD_Req_Attr.STRING) or (attr_list[0].attr_id == LDMSD_Req_Attr.JSON):
                msg = attr_list[0].attr_value
        elif len(attr_list) == 0:
            attr_list = None
        return {'errcode': errcode, 'msg': msg, 'attr_list': attr_list}

    def is_error_resp(self, json_obj_resp):
        if json_obj_resp == 0:
            return False

        if len(json_obj_resp) == 1:
            if 'error' in json_obj_resp.keys():
                return True
        elif len(json_obj_resp) > 1:
            if 'error' in json_obj_resp[0].keys():
                return True
        return False

    def resp2json(self, resp):
        return json.dumps(resp)

    @classmethod
    def from_verb_attrs(cls, verb, attrs):
        """Create LDMSD_Request object from verb (str) and attrs (list of str pair)

        verb (str) - the LDMSD command verb
        attrs (list of (str, str)) - the list of attribute-value pairs. For
                positional attribute, the value is None.

        """
        req_attrs = []
        attr_s = []
        for a, v in attrs:
            s = a if v is None else a+"="+v
            if (verb == "config" and a != "name") or (verb == "env"):
                attr_s.append(s)
            else:
                try:
                    attr = LDMSD_Req_Attr(value = v, attr_name = a)
                except KeyError:
                    attr_s.append(s)
                except Exception:
                    raise
                else:
                    req_attrs.append(attr)
        if attr_s:
            attr_str = " ".join(attr_s)
            attr = LDMSD_Req_Attr(value = attr_str, attr_id = LDMSD_Req_Attr.STRING)
            req_attrs.append(attr)
        req_attrs.append(LDMSD_Req_Attr(attr_id = LDMSD_Req_Attr.LAST))
        return LDMSD_Request(command = verb, attrs = req_attrs)

    ATTR_RE = re.compile("([^=]+)(?:=(.+))?")

    @classmethod
    def from_str(cls, cmd_str):
        """Parse the cmd_str and make LDMSD_Request object from it

        cmd_str - a string in the `verb arg1=val1 arg2=val2 ...` format.
        """
        tkns = re.split("\s+", cmd_str)
        verb = tkns[0]
        av_list = (cls.ATTR_RE.match(x).groups() for x in tkns[1:])
        return cls.from_verb_attrs(verb, av_list)

cmd_line_options = {'a': "default-auth",
                    'B': "banner",
                    'H': "hostname",
                    'k': "publish-kernel",
                    'l': "logfile",
                    'm': "mem",
                    'n': "daemon-name",
                    'P': "num-threads",
                    'r': "pidfile",
                    's': "kernel-file",
                    'v': "loglevel",
                    'x': "xprt"           }

def cmd_line_attr_name_get(s = None, l = None):
    if s is not None:
        return cmd_line_options[s]
    if l is not None:
        return cmd_line_options.keys()[cmd_line_options.values().index(l)]

def cmd_line_options_supported_get():
    return cmd_line_options

class LdmsdReqCmd(cmd.Cmd):
    def __init__(self, host = None, port = None, infile=None):
        try:
            self.ctrl = ldmsd_config.ldmsdInetConfig(host = host,
                                                     port = int(port))
            self.prompt = "{0}:{1}> ".format(host, port)

            if infile:
                cmd.Cmd.__init__(self, stdin=infile)
            else:
                cmd.Cmd.__init__(self)
        except:
            raise

    def do_quit(self, arg):
        """
        Quit the ldmsd_request interface
        """
        self.ctrl.close()
        return True

    def complete_prdcr_set(self, text, line, begidx, endidx):
        attr_list = ['prdcr']
        return ["{0}=".format(attr) for attr in attr_list if attr.startswith(text)]


    def do_prdcr_set(self, arg):
        """
        Print the list of producer sets of a producer and their status
        """
        try:
            prdcr_name = LDMSD_Req_Attr(LDMSD_Req_Attr.PRODUCER, arg.split("=")[1])
            req = LDMSD_Request(LDMSD_Request.PRDCR_METRIC_SET, attrs = [prdcr_name,])
            req.send(self.ctrl.socket)
            metric_sets = req.receive(self.ctrl.socket)
            metric_sets = json.loads(metric_sets)
            if req.is_error_resp(metric_sets):
                print("Error: {0}".format(metric_sets[0]['error']))
            else:
                print("Name             Schema Name      State")
                print("---------------- ---------------- ------------ ")
                for pset in metric_sets:
                    print("    {0:16} {1:16} {2}".format(pset['inst_name'],
                                                         pset['schema_name'],
                                                         pset['state']))
        except:
            raise

    def do_prdcr_add(self, arg):
        """
        Add a producer.
        """
        pass

if __name__ == "__main__":
    is_debug = True
    try:
        parser = argparse.ArgumentParser(description="Configure an LDMS Daemon.")
        parser.add_argument("--host", help = "Hostname of ldmsd to connect to")
        parser.add_argument('--port',
                            help = "Inet ctrl listener port of ldmsd")
        parser.add_argument('--debug', action = "store_true",
                            help = argparse.SUPPRESS)
        args = parser.parse_args()
        is_debug = args.debug

        if args.host is None or args.port is None:
            print("Please give --host and --port")
            sys.exit(1)

        reqParser = LdmsdReqCmd(host = args.host, port = args.port)

        reqParser.cmdloop("Welcome to the LDMSD control processor")

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        if is_debug:
            print(is_debug)
            traceback.print_exc()
            sys.exit(2)
        else:
            print(e)

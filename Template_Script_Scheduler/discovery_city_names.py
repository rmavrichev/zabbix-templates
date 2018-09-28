#!/usr/bin/env python

import sys,socket
import json
import packetlogic2

# Usage:
# ./discovery_city_names.py "10.78.139.218"
# ./discovery_city_names.py 10.78.139.218

# JSON data list:
data = []

# Procera specific:
user = "test"
pwd = "test"

# define Check input:
def getOptions():
    global host_list
    if len(sys.argv[1:]) >= 1:
        host_list = sys.argv[1:]
        #print host_list
        for host in host_list:
            if host <> '':
                try:
                    # legal IP:
                    socket.inet_aton(host)
                except socket.error:
                    # illegal IP:
                    print 'Error! Input [%s] is NOT IP address' % (host)
                    raise SystemExit
    else:
        print 'Usage: %s <ip_addr>' % sys.argv[0]
        raise SystemExit


#Define some magic from procera:
def getNetObjectsList(address,username,password,path):
    global rt
    try:
        pl = packetlogic2.connect(address,username,password)
    except IOError:
        print 'Error! Connect fail to: %s' % host
        sys.exit(1)
    except RuntimeError:
        print 'Error! Authentication fail to: %s' % host
        sys.exit(1)

    rs = pl.Ruleset()
    for net_object in rs.object_list('/NetObjects' + path, recursive=False):
        # Debug:
        #print net_object.name
        data.append({'{#CITY_NAME}': net_object.name})

# parse input options:
getOptions()


#debug:
#print(host_list)

#Get data from procera:
host = host_list[0]
getNetObjectsList(host, user, pwd, "/Core")

### generate output like this:
### {"data": [{"{#CITY_NAME}": "Voice"}, {"{#CITY_NAME}": "ABC"}]}

print json.dumps({"data": data})

############################# EOF #############################

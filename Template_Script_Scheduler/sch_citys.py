#!/usr/bin/env python

import os,sys,time,socket
import packetlogic2

# Usage:
# ./sch_citys.py "spb-pl20k1.scartel.dc" "10.78.139.218" "10.78.139.219" "" ""
# ./sch_citys.py spb-pl20k1.scartel.dc 10.78.139.218 10.78.139.219

# Zabbix specific:
ZBXSENDER = '/usr/bin/zabbix_sender'
ZBXSERVER = '127.0.0.1'
TSTAMP = str(int(time.time()))
VALUE = '0'

# Procera specific:
user = "test"
pwd = "test"
counter1 = 0
skip = 3
rt = None

total_speed = {}
default = (0, 0)

# define Chechk input:
def getOptions():
    global host_list
    global ZBXHOST
    if len(sys.argv[1:]) >= 1:
        ZBXHOST = sys.argv[1]
        host_list = sys.argv[2:]
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
        print 'Usage: %s <ZBXHOST> <ip_addr1> <ip_addr2> <ip_addrN>' % sys.argv[0]
        raise SystemExit


#Define some magic from procera:
def update(A, B):
    return A[0] + B[0], A[1] + B[1]

def getAggrView(address,username,password,path):
    global rt
    try:
        pl = packetlogic2.connect(address,username,password)
    except IOError:
        print 'Error! Connect fail to: %s' % host
        sys.exit(1)
    except RuntimeError:
        print 'Error! Authentication fail to: %s' % host
        sys.exit(1)

    rt = pl.Realtime()
    v = rt.get_view_builder()
    v.distribution("NetObject Level", path)
    rt.add_aggr_view_callback(v, view_callback)
    rt.update_forever(5)

def view_callback(data):
    # ['_children', 'parentid', 'data', '_rawname', '_name']
    global counter1
    global rt
    global total_speed
    global default
    global obj_filter

    if counter1 == skip:
        for dat in data._children:
            total_speed[dat._name] = update(total_speed.get(dat._name, default), dat.data['speed'])
        rt.stop_updating()
    counter1 += 1



# parse input options:
getOptions()

# call Procera_magic:
for host in host_list:
    if host <> '':
        counter1 = 0
        getAggrView(host, user, pwd, "/Core")

for city, speed in total_speed.items():
    if city not in ['<Ungrouped>', '<Unresolved>']:
        speed = total_speed.get(city,default)
        # Debug:
        #print '%s_downlink:%d    %s_uplink:%d' % (city, speed[0]/8, city, speed[1]/8)

        # define ZBX values:
        VAL_DL = str(speed[0] / 8)
        VAL_UL = str(speed[1] / 8)
        CITY_NAME = str(city)

        # Create ZBX sender strings:
        tstmp = ZBXSENDER + ' -z ' + ZBXSERVER + ' -s ' + ZBXHOST + ' -k PrcrCity.tstamp.[' + CITY_NAME + '] -o ' + TSTAMP
        valdl = ZBXSENDER + ' -z ' + ZBXSERVER + ' -s ' + ZBXHOST + ' -k PrcrCity.val_dl.[' + CITY_NAME + '] -o ' + VAL_DL
        valul = ZBXSENDER + ' -z ' + ZBXSERVER + ' -s ' + ZBXHOST + ' -k PrcrCity.val_ul.[' + CITY_NAME + '] -o ' + VAL_UL

        # for debug
        #print(tstmp)
        #print(valdl)
        #print(valul)

        # call ZBX sender:
        os.system(tstmp)
        os.system(valdl)
        os.system(valul)

############################# EOF #############################

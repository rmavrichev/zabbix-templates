#!/usr/bin/env python

import os,sys,time,socket
import packetlogic2

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
            #print '%s' % (host)
    else:
        print 'Usage: %s <ZBXHOST> <ip_addr1> <ip_addr2> <ip_addrN>' % sys.argv[0]
        raise SystemExit


#Define some magic from procera:
def update(A, B):
    return A[0] + B[0], A[1] + B[1]

def getAggrView(address,username,password,path):
    global rt
    #text_file = open("/tmp/host.txt", "a")
    #text_file.write("ip: %s\n" % address)
    #text_file.close()
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


    if counter1 == skip:
        for dat in data._children:
            # print "%s %s" % (dat._name, "%d %d" % dat.data['speed'])
            total_speed[dat._name] = update(total_speed.get(dat._name,default), dat.data['speed'])
        rt.stop_updating()
    counter1 += 1



# parse input options:
getOptions()

# call Procera_magic:
for host in host_list:
    if host <> '':
        #print(host)
        counter1 = 0
        getAggrView(host, user, pwd, "/")

speed = total_speed.get("<Ungrouped>",default)

# total ungroup on host(s):
VALUE = str(speed[0]/8 + speed[1]/8)

makeitastring = ','.join(map(str, host_list))


# Create ZBX sender strings:
tstmp = ZBXSENDER + ' -z ' + ZBXSERVER + ' -s ' + ZBXHOST + ' -k PrcrUngr.tstamp -o ' + TSTAMP
value = ZBXSENDER + ' -z ' + ZBXSERVER + ' -s ' + ZBXHOST + ' -k PrcrUngr.value -o ' + VALUE
echoe = ZBXSENDER + ' -z ' + ZBXSERVER + ' -s ' + ZBXHOST + ' -k PrcrUngr.echo -o '  + makeitastring

#print(tstmp)
#print(value)
#print(echoe)

# call ZBX sender:
os.system(tstmp)
os.system(value)
os.system(echoe)

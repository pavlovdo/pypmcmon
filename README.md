Description
===========
Zabbix Pacemaker Cluster Monitoring via pcs xml status reading

Tested with Cent OS 8, Pacemaker 2.0.x, pcs 0.10


Requirements
============

1) python >= 3.6

2) pcs: pacemaker cluster cli utility

3) zabbix-server (tested with versions 4.4-5.2)

4) python module py-zabbix: sending traps to zabbix


Installation
============
1) Clone pypmcmon repo to directory /etc/zabbix/externalscripts to each node of cluster (where you want to get status via pcs):
```
sudo mkdir -p /etc/zabbix/externalscripts
sudo git clone https://github.com/pavlovdo/pypmcmon /etc/zabbix/externalscripts/pypmcmon
cd /etc/zabbix/externalscripts/pypmcmon
```

2) A) Check execute permissions for scripts:
```
ls -l *.py *.sh
```
B) If not:
```
sudo chmod +x *.py *.sh
```

3) Change example configuration file pyipmimon.conf: login, password, address of zabbix_server;

4) Check run pcs status:
```
/sbin/pcs status
```
You have to view status of your cluster. If not, check pcs installation and permissions to run pcs from this node.


5) Check configuration and running zabbix trappers on your zabbix server or proxy:
```
### Option: StartTrappers
#       Number of pre-forked instances of trappers.
#       Trappers accept incoming connections from Zabbix sender, active agents and active proxies.
#       At least one trapper process must be running to display server availability and view queue
#       in the frontend.
#
# Mandatory: no
# Range: 0-1000
# Default:
# StartTrappers=5
```
```
# ps aux | grep trapper
zabbix    776389  0.2  0.4 2049416 111772 ?      S    дек07  63:41 /usr/sbin/zabbix_server: trapper #1 [processed data in 0.000166 sec, waiting for connection]
zabbix    776390  0.2  0.4 2049512 112016 ?      S    дек07  63:43 /usr/sbin/zabbix_server: trapper #2 [processed data in 0.000342 sec, waiting for connection]
zabbix    776391  0.2  0.4 2049452 112092 ?      S    дек07  63:12 /usr/sbin/zabbix_server: trapper #3 [processed data in 0.000301 sec, waiting for connection]
zabbix    776392  0.2  0.4 2049600 112064 ?      S    дек07  63:57 /usr/sbin/zabbix_server: trapper #4 [processed data in 0.000187 sec, waiting for connection]
zabbix    776393  0.2  0.4 2049412 111836 ?      S    дек07  63:31 /usr/sbin/zabbix_server: trapper #5 [processed data in 0.000176 sec, waiting for connection]
```

6) Import template Pacemaker Cluster Pypmcmon.json to Zabbix, if use Zabbix 5.2,
and template Template Pacemaker Cluster Pypmcmon.xml (no more support) for Zabbix 4.4;

7) Create your node hosts in Zabbix and link template to them.
In host configuration set parameters "Host name" and "IP address" for Agent Interface.
Use the same hostname as in the file pypmcmon.conf, node1.example.com for example.

8) Further you have options: run scripts from host or run scripts from docker container.

If you want to run scripts from host:

A) Install Python 3 and pip3 if it is not installed;

B) Install required python modules:
```
pip3 install -r requirements.txt
```

C) Create cron job to get pcs status and send data to zabbix:
```
echo "*/1 * * * * /sbin/pcs status xml > /etc/zabbix/externalscripts/pypmcmon/data/pmc_status.xml && /etc/zabbix/externalscripts/pypymcmon/pypmcmon.py > /dev/null" >> /tmp/crontab && \
crontab /tmp/crontab && rm /tmp/crontab
```

If you want to run scripts from docker container:

A) Run build.sh:
```
cd /etc/zabbix/externalscripts/pypymcmon
./build.sh
```

B) Run dockerrun.sh;
```
./dockerrun.sh
```


Notes
======
1) For send exception alarms via slack hook to your slack channel, set parameter slack_hook in conf.d/pypypmcmon.conf.
More details in https://api.slack.com/messaging/webhooks


Tested
======
Cent OS 8, Pacemaker 2.0.x, pcs 0.10
Zabbix 4.4, 5.2


Related Links
=============
https://github.com/ClusterLabs/pcs

https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/configuring_and_managing_high_availability_clusters/assembly_pcs-operation-configuring-and-managing-high-availability-clusters

https://github.com/adubkov/py-zabbix

https://api.slack.com/messaging/webhooks

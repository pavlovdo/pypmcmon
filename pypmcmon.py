#!/usr/bin/env python3

#
# Pacemaker cluster components discovery and sending status to Zabbix
#
# 2020-2021 Denis Pavlov
#
# Discover pacemaker cluster nodes, fence devices, clones and resources via pcs status and sends their status to Zabbix Server via Zabbix Sender API
#
# Use with zabbix template Pacemaker Cluster Pypmcmon
#

import os
import sys
import xml.etree.ElementTree as ET

from configread import configread
from functions import zabbix_send
from json import dumps, load
from pyzabbix import ZabbixMetric


# set project as current directory name, software as name of current script
project = os.path.abspath(__file__).split('/')[-2]
software = sys.argv[0]

# get config file name
conf_file = '/etc/zabbix/externalscripts/{project}/conf.d/{project}.conf'

# read network device parameters from config and save it to dict
nd_parameters = configread(conf_file, 'NetworkDevice', 'hostname', 'printing')

# read parameters of cluster and alerting from config file and save it to dict
pmc_parameters = configread(conf_file, 'PM Cluster', 'fence_agent',
                            'pmc_status_file', 'pmc_structure_file')

# get hostname of host for send with zabbix trapper
hostname = nd_parameters['hostname']

# get printing boolean variable from config for debugging enable/disable
printing = eval(nd_parameters['printing'])


def zabbix_discovery_send(zd_name, co_type, zd_macro_co_name, co_name):
    """ create discovery and send to zabbix server """

    # initialize packet for zabbix
    packet = []

    # set key as discovery name
    trapper_key = zd_name
    # create json for zabbix discovery trapper value
    trapper_value = dumps(
        [{'{#OBJECT_TYPE}': co_type, zd_macro_co_name: co_name}])

    # print data for visual check
    if printing:
        print('hostname: ', hostname)
        print('trapper_key: ', trapper_key)
        print('trapper_value: ', trapper_value)

    # add data to packet for zabbix
    packet.append(ZabbixMetric(hostname, trapper_key, trapper_value))

    # trying send data to zabbix
    zabbix_send(packet, printing, software)


def zabbix_items_values_send(element, co_type, attributes, co_name):
    """ send items values to zabbix server """

    packet = []

    # get values of attributes and save it to packet for zabbix
    for attr_name in attributes:
        attr_value = element.get(attr_name)

        trapper_key = f'{attr_name}[{co_name}]'

        # convert boolean to binary values for decrease zabbix db and draw graphs
        if attr_value == 'true':
            trapper_value = 1
        elif attr_value == 'false':
            trapper_value = 0
        else:
            trapper_value = attr_value

        # print data for visual check
        if printing:
            print('hostname: ', hostname)
            print('trapper_key: ', trapper_key)
            print('trapper_value: ', trapper_value)

        # form list of data for sending to zabbix
        packet.append(ZabbixMetric(hostname, trapper_key, trapper_value))

        # trying send data to zabbix
        zabbix_send(packet, printing, software)


def main():

    # create cluster objects dictionary, where values are lists with xml tags and attributes
    with open(pmc_parameters['pmc_structure_file'], "r") as co_structure_file:
        cluster_objects = load(co_structure_file)

    # Parse PM cluster XML status file (set path to file in pypmcmon conf file and macro in Zabbix Template App Pacemaker Cluster)
    # create and renew cluster XML status file via execute "pcs status xml" from shell
    tree = ET.parse(pmc_parameters['pmc_status_file'])
    root = tree.getroot()

    # iterate over dict of cluster objects
    for co_type in cluster_objects:
        # create list of xml elements of cluster object type
        xml_elements_co = root.findall(cluster_objects[co_type]['xml_element'])
        # define xml attribute of name of cluster object type
        co_name_attr = cluster_objects[co_type]['xml_attr_name']
        # iterate over cluster objects of one type
        for xml_element_co in xml_elements_co:
            # get name of cluster object
            co_name = xml_element_co.get(co_name_attr)
            # create and send discovery of cluster objects
            if 'zabbix_discovery_name' and 'zabbix_discovery_macro' in cluster_objects[co_type]:
                zd_name = cluster_objects[co_type]['zabbix_discovery_name']
                zd_macro_co_name = cluster_objects[co_type]['zabbix_discovery_macro']
                zabbix_discovery_send(
                    zd_name, co_type, zd_macro_co_name, co_name)
            co_attr_names = cluster_objects[co_type]['xml_attributes']
            zabbix_items_values_send(
                xml_element_co, co_type, co_attr_names, co_name)

            # check objects for group existing
            xml_element_co_groups = xml_element_co.findall('./group')
            if len(xml_element_co_groups):
                for xml_element_co_group in xml_element_co_groups:
                    # get name of cluster group of resources
                    co_group_name = xml_element_co_group.get('id')
                    # create list of xml elements of cluster group resources
                    xml_element_co_group_resources = xml_element_co_group.findall(
                        './resource')
                    for xml_element_co_group_resource in xml_element_co_group_resources:
                        group_resource_name = xml_element_co_group_resource.get(
                            'id') + '.' + co_group_name
                        # create and send discovery of cluster group resources
                        group_resource_type = xml_element_co_group_resource.get(
                            'resource_agent')
                        for co_type in cluster_objects:
                            if group_resource_type in cluster_objects[co_type]['xml_element']:
                                if 'zabbix_discovery_name' and 'zabbix_discovery_macro' in cluster_objects[co_type]:
                                    zd_name = cluster_objects[co_type]['zabbix_discovery_name']
                                    zd_macro_co_name = cluster_objects[co_type]['zabbix_discovery_macro']
                                    zabbix_discovery_send(
                                        zd_name, co_type, zd_macro_co_name, group_resource_name)
                        # get list of resource attributes, based on virtual domain
                        resource_attr_names = cluster_objects['virtual domain']['xml_attributes']
                        zabbix_items_values_send(
                            xml_element_co_group_resource, co_type, resource_attr_names, group_resource_name)


if __name__ == "__main__":
    main()

#! /usr/bin/python
from lxml import etree
import xml.etree.ElementTree as ET

from jnpr.junos import Device


# newline stripper function
def ns ( stringIn ):

    stringHalf = stringIn.lstrip()

    stringOut = stringHalf.rstrip()

    return stringOut

def routeFinder ( device_connection, table_name, route = "0.0.0.0/0" ):

    route_info = device_connection.rpc.get_route_information(destination=route, exact=True, table=table_name)

    route_info_finder = route_info.findall('route-table/rt/rt-destination')

    route_found = route_info_finder[0].text

    route_nh_addr_finder = route_info.findall('route-table/rt/rt-entry/nh/to')

    nh_addr_found = route_nh_addr_finder[0].text

    route_nh_if_finder = route_info.findall('route-table/rt/rt-entry/nh/via')

    route_nh_addr_found = route_nh_if_finder[0].text

    return {"table" : table_name, "route": route_found ,  "nh_addr": nh_addr_found , "nh_if" : route_nh_addr_found }


def ifstats (device_connection, ifName ):

    collect_interface_stats = device_connection.rpc.get_interface_information(interface_name=ifName, statistics=True, detail=True)

    input_bps_finder = collect_interface_stats.findall('logical-interface/transit-traffic-statistics/input-bps')

    # strip the newlines from the returned value
    ibps = ns ( input_bps_finder[0].text )

    input_pps_finder = collect_interface_stats.findall('logical-interface/transit-traffic-statistics/input-pps')

    # strip the newlines from the returned value
    ipps = ns ( input_pps_finder[0].text )

    output_bps_finder = collect_interface_stats.findall('logical-interface/transit-traffic-statistics/output-bps')

    # strip the newlines from the returned value
    obps = ns ( output_bps_finder[0].text )

    output_pps_finder = collect_interface_stats.findall('logical-interface/transit-traffic-statistics/output-pps')

    # strip the newlines from the returned value
    opps = ns ( output_pps_finder[0].text )

    return { "interface" : ifName, "ibps": ibps ,  "ipps": ipps , "obps" : obps , "opps" : opps }


def if_fw_state_count (device_connection, ifName ):
    collect_fw_state_count = device_connection.rpc.get_flow_session_information(interface=ifName)

    fw_state_count_finder = collect_fw_state_count.findall('displayed-session-count')

    fw_state_count = ns(fw_state_count_finder[0].text)

    return { "interface" : ifName , "state_count" : fw_state_count  }


def if_fw_states (device_connection, ifName ):
    collect_fw_states = device_connection.rpc.get_flow_session_information(interface=ifName)

    fw_state_finder = collect_fw_states.findall('flow-session')

    all_states = []

    #root = collect_fw_states.getroot()
    for states in collect_fw_states:

        state = {}

        session_id = states.xpath('./session-identifier/text()')

        if len ( session_id ) > 0:
            session_id = ns(session_id[0])

        state["id"] = session_id

        app_name = states.xpath('./dynamic-application-name/text()')

        if len(app_name) > 0:
            app_name = ns(app_name[0])

        state["app_name"] = app_name

        source_ip = states.xpath('./flow-information/source-address/text()')

        if len(source_ip) > 0:
            source_ip = ns(source_ip[0])

        state["source_ip"] = source_ip

        destination_ip = states.xpath('./flow-information/destination-address/text()')

        if len(destination_ip) > 0:
            destination_ip = ns(destination_ip[0])

        state["destination_ip"] = destination_ip

        destination_port = states.xpath('./flow-information/destination-port/text()')

        if len(destination_port) > 0:
            destination_port = ns(destination_port[0])

        state["destination_port"] = destination_port

        source_port = states.xpath('./flow-information/source-port/text()')

        if len(source_port) > 0:
            source_port = ns(source_port[0])

        state["source_port"] = source_port

        if len(state["destination_ip"]) >= 1 and len(state["source_ip"]) >= 1 :
            all_states.append(state)

    return all_states



def collectRPMStats(device_connection):
    print "collecting RPM probe stats"

    collect_rpm_stats = device_connection.rpc.get_probe_results()

    target_address = collect_rpm_stats.xpath("./probe-test-results/target-address/text()")[0]

    target_interface = collect_rpm_stats.xpath("./probe-test-results/destination-interface/text()")[0]

    current_probes_sent = collect_rpm_stats.xpath("./probe-test-results/probe-test-current-results/probe-test-generic-results/probes-sent/text()")[0]

    current_probes_received = collect_rpm_stats.xpath("./probe-test-results/probe-test-current-results/probe-test-generic-results/probe-responses/text()")[0]

    current_probes_percent_lost = collect_rpm_stats.xpath("./probe-test-results/probe-test-current-results/probe-test-generic-results/loss-percentage/text()")[0]

    last_probes_sent = collect_rpm_stats.xpath("./probe-test-results/probe-last-test-results/probe-test-generic-results/probes-sent/text()")[0]

    last_probes_received = collect_rpm_stats.xpath("./probe-test-results/probe-last-test-results/probe-test-generic-results/probe-responses/text()")[0]

    last_probes_percent_lost = collect_rpm_stats.xpath("./probe-test-results/probe-last-test-results/probe-test-generic-results/loss-percentage/text()")[0]

    rpm_results = { "target_address" : target_address , "target_interface" : target_interface , "current_probes_sent" : current_probes_sent, "current_probes_received" : current_probes_received, "current_probes_percent_lost" : current_probes_percent_lost, "last_probes_sent" : last_probes_sent, "last_probes_received" : last_probes_received, "last_probes_percent_lost" : last_probes_percent_lost}

    return rpm_results




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


def if_fw_state (device_connection, ifName ):
    collect_fw_state_count = device_connection.rpc.get_flow_session_information(interface=ifName)

    fw_state_count_finder = collect_fw_state_count.findall('displayed-session-count')

    print fw_state_count_finder

    fw_state_count = ns(fw_state_count_finder[0].text)

    print { "interface" : ifName , "state_count" : fw_state_count }

    return { "interface" : ifName , "state_count" : fw_state_count  }


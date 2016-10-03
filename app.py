#! /usr/bin/python

from lxml import etree
import xml.etree.ElementTree as ET
import flask
import time
import thread
import time



from jnpr.junos import Device
from pprint import pprint
from jnpr.junos.op.ethport import EthPortTable

from jnpr.junos.op.routes import RouteTable


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


device_stats = {}


def collectStats (devices):

    print "collecting stats"

    global device_stats

    gr_stat_dict = ifstats(d, "gr-0/0/0.0")

    #print gr_stat_dict

    device_stats["gr_if"] = gr_stat_dict

    st_stat_dict = ifstats(d, "st0.0")

    device_stats["st_if"] = st_stat_dict

    inet0_dict = routeFinder(d, "inet.0")

    device_stats["inet0"] = inet0_dict

    app_route_dict = routeFinder(d, "app-route-inet.inet.0")

    device_stats["approute"] = app_route_dict



    print device_stats


def statLoop (devices):

    while True:

        collectStats(devices)

        time.sleep(5)


devices = []

devices.append( Device(host='192.168.57.2', user='root', password='Welcome!') )

for d in devices:
    try:
        d.open()
    except:
        print "Connection to device failed."


thread.start_new_thread( statLoop , (devices,)  )


app = flask.Flask(__name__)

@app.route('/')

def index():

    return_string = ""
    for i in device_stats:
        return_string = return_string + i
        return_string = return_string + "\n"


    return '''
    <html>
    <head>
    <title> SD-WAN Stats </title>
    </head>
    <body>
    <table>
    <tr>
    <td><u>''' + device_stats["inet0"]["table"] + '''</u></td>
    <td><u>''' + device_stats["approute"]["table"] + '''</u></td>
    </tr>
    <tr>
    <td>''' + device_stats["inet0"]["route"] + '''</td>
    <td>''' + device_stats["approute"]["route"] + '''</td>
    </tr>
    <tr>
    <td>''' + device_stats["inet0"]["nh_if"] + '''</td>
    <td>''' + device_stats["approute"]["nh_if"] + '''</td>
    </tr>
    <tr></tr>
    <tr></tr>
    <tr>
    <td>
    <table>

    <tr><td><u> ''' + device_stats["inet0"]["nh_if"] + '''</u></tr></td>
    <tr><td>In BPS: ''' + device_stats["gr_if"]["ibps"]  + ''' </tr></td>
    <tr><td>In PPS: ''' + device_stats["gr_if"]["ipps"]  + ''' </tr></td>
    <tr><td>Out BPS: ''' + device_stats["gr_if"]["obps"]  + ''' </tr></td>
    <tr><td>Out PPS: ''' + device_stats["gr_if"]["opps"]  + ''' </tr></td>

    </table>
    </td>
    <td>
    <table>

    <tr><td><u> ''' + device_stats["approute"]["nh_if"] + '''</u></tr></td>
    <tr><td>In BPS: ''' + device_stats["st_if"]["ibps"]  + ''' </tr></td>
    <tr><td>In PPS: ''' + device_stats["st_if"]["ipps"]  + ''' </tr></td>
    <tr><td>Out BPS: ''' + device_stats["st_if"]["obps"]  + ''' </tr></td>
    <tr><td>Out PPS: ''' + device_stats["st_if"]["opps"]  + ''' </tr></td>

    </table>
    </td>
    </tr>
    </table>
    <body>
    </html>



    '''


app.run(debug=True, port=8000, host='0.0.0.0')
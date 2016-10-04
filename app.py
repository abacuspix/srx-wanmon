#! /usr/bin/python

from lxml import etree
import xml.etree.ElementTree as ET
import flask
import time
import thread
import time

from flask import jsonify



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



def statLoop (devices):

    while True:

        collectStats(devices)

        time.sleep(5)


devices = []

devices.append( Device(host='172.16.237.98', user='root', password='Welcome!') )

for d in devices:
    try:
        d.open()
    except:
        print "Connection to device failed."


thread.start_new_thread( statLoop , (devices,)  )


app = flask.Flask(__name__)

@app.route('/_get_statistics')
def get_statistics():
    print "running get statistics api"

    return jsonify( inet_table=device_stats["inet0"]["table"] , inet_route = device_stats["inet0"]["route"] , inet_route_nh = device_stats["inet0"]["nh_if"] , alt_table=device_stats["approute"]["table"] , alt_table_route = device_stats["approute"]["route"] , alt_table_nh = device_stats["approute"]["nh_if"] , gr_if_ibps = device_stats["gr_if"]["ibps"] , gr_if_ipps = device_stats["gr_if"]["ipps"] , gr_if_obps = device_stats["gr_if"]["obps"] , gr_if_opps =  device_stats["gr_if"]["opps"] , st_if_ibps = device_stats["st_if"]["ibps"] , st_if_ipps = device_stats["st_if"]["ipps"] , st_if_obps = device_stats["st_if"]["obps"] , st_if_opps = device_stats["st_if"]["opps"] )

@app.route('/')
def index():
    return '''
    <html>
    <head>
    <title> SD-WAN Stats </title>

    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>

    </head>

    <body>


    <table>
    <tr>
    <td><u><div id="inettable"></div></u></td>
    <td><u><div id="alttable"></div></u></td>
    </tr>
    <tr>
    <td><div id="inetroute"></div></td>
    <td><div id="altroute"></div></td>
    </tr>
    <tr>
    <td><div id="inet_route_nh"></div></td>
    <td><div id="alt_route_nh"></div></td>
    </tr>
    <tr></tr>
    <tr></tr>
    <tr>
    <td>
    <table>

    <tr><td><u><div id="inet_route_nh"></div></u></tr></td>
    <tr><td>In BPS: <div id="gr_if_ibps"></div> </tr></td>
    <tr><td>In PPS: <div id="gr_if_ipps"></div> </tr></td>
    <tr><td>Out BPS: <div id="gr_if_obps"></div> </tr></td>
    <tr><td>Out PPS: <div id="gr_if_opps"></div> </tr></td>

    </table>
    </td>
    <td>
    <table>

    <tr><td><u><div id="alt_route_nh"></div></u></tr></td>
    <tr><td>In BPS: <div id="st_if_ibps"></div> </tr></td>
    <tr><td>In PPS: <div id="st_if_ipps"></div> </tr></td>
    <tr><td>Out BPS: <div id="st_if_obps"></div> </tr></td>
    <tr><td>Out PPS: <div id="st_if_opps"></div> </tr></td>

    </table>
    </td>
    </tr>
    </table>


    <script type=text/javascript>

    setInterval(
        function()
            {

                $.getJSON("/_get_statistics",
                {},
                function(data) {
                    $("#inettable").text(data.inet_table);
                    $("#alttable").text(data.alt_table);

                    $("#inetroute").text(data.inet_route);
                    $("#altroute").text(data.alt_table_route);

                    $("#inet_route_nh").text(data.inet_route_nh);
                    $("#alt_route_nh").text(data.alt_table_nh);

                    $("#gr_if_ibps").text(data.gr_if_ibps);
                    $("#gr_if_obps").text(data.gr_if_obps);
                    $("#gr_if_ipps").text(data.gr_if_ipps);
                    $("#gr_if_opps").text(data.gr_if_opps);

                    $("#st_if_ibps").text(data.st_if_ibps);
                    $("#st_if_obps").text(data.st_if_obps);
                    $("#st_if_ipps").text(data.st_if_ipps);
                    $("#st_if_opps").text(data.st_if_opps);



                });
            },
            1000);
    </script>
    </body>
    </html>

    '''

app.run(debug=True, port=8000, host='0.0.0.0')
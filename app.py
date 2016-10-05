#! /usr/bin/python

from lxml import etree
import xml.etree.ElementTree as ET
import flask
import time
import thread
import time


from srx_wanmon_utils import if_fw_state_count, ifstats, routeFinder, if_fw_states

from flask import jsonify

from jnpr.junos import Device



device_stats = {}


def collectStats (device):

    global device_stats

    gr_stat_dict = ifstats(device, "gr-0/0/0.0")

    #print gr_stat_dict

    device_stats["gr_if"] = gr_stat_dict

    st_stat_dict = ifstats(device, "st0.0")

    device_stats["st_if"] = st_stat_dict

    inet0_dict = routeFinder(device, "inet.0")

    device_stats["inet0"] = inet0_dict

    app_route_dict = routeFinder(device, "app-route-inet.inet.0")

    device_stats["approute"] = app_route_dict

    device_stats["prime_if_fw_state_count"] = if_fw_state_count(device , "gr-0/0/0.0")

    device_stats["alt_if_fw_state_count"] = if_fw_state_count(device , "st0.0")


def collectSessions (device):

    device_sessions = {}

    device_sessions["gr-0/0/0.0"] = if_fw_states (device, "gr-0/0/0.0")

    device_sessions["st0.0"] = if_fw_states(device, "st0.0")

    return  device_sessions

device_sessions = {}

def statLoop (device):

    global device_sessions

    while True:

        collectStats(device)

        device_sessions = collectSessions (device)

        time.sleep(5)


devices = []

devices.append( Device(host='192.168.57.2', user='root', password='Welcome!') )

for d in devices:
    try:
        d.open()
    except:
        print "Connection to device failed."


thread.start_new_thread( statLoop , (d,)  )


app = flask.Flask(__name__)


@app.route('/_get_sessions')
def get_sessions():
    return jsonify( device_sessions )


@app.route('/_get_statistics')
def get_statistics():
    return jsonify( alt_if_fw_state_count = device_stats["alt_if_fw_state_count"]["state_count"] , prime_if_fw_state_count = device_stats["prime_if_fw_state_count"]["state_count"], inet_table=device_stats["inet0"]["table"] , inet_route = device_stats["inet0"]["route"] , inet_route_nh = device_stats["inet0"]["nh_if"] , alt_table=device_stats["approute"]["table"] , alt_table_route = device_stats["approute"]["route"] , alt_table_nh = device_stats["approute"]["nh_if"] , gr_if_ibps = device_stats["gr_if"]["ibps"] , gr_if_ipps = device_stats["gr_if"]["ipps"] , gr_if_obps = device_stats["gr_if"]["obps"] , gr_if_opps =  device_stats["gr_if"]["opps"] , st_if_ibps = device_stats["st_if"]["ibps"] , st_if_ipps = device_stats["st_if"]["ipps"] , st_if_obps = device_stats["st_if"]["obps"] , st_if_opps = device_stats["st_if"]["opps"] )

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
    <br>
    <br>
    <table>
    <tr>
    <td>Primary WAN Session Count</td>
    <td>Alternate WAN Session Count</td>
    </tr>
    <tr>
    <td><div id="prime_if_fw_state_count"></div</td>
    <td><div id="alt_if_fw_state_count"></div></td>
    </tr>
    </table>
    <br>
    <br>
    <br>
    <table id="stateTable">

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

                    $("#prime_if_fw_state_count").text(data.prime_if_fw_state_count);
                    $("#alt_if_fw_state_count").text(data.alt_if_fw_state_count);
                });
            },
            1000);
    </script>


    <script type=text/javascript>
        setInterval(
        function()
            {
            $.getJSON("/_get_sessions", function (data) {

                var stateTable = document.getElementById("stateTable")

                stateTable.innerHTML = "";

                $.each( data, function( interface, state ) {




                    var interface_tr = document.createElement("tr");

                    var interface_td_label = document.createElement("td");
                    var interface_td_label_text = document.createTextNode( "Interface:" );

                    interface_td_label.appendChild( interface_td_label_text );

                    var interface_td = document.createElement("td");
                    var interface_td_text = document.createTextNode( JSON.stringify(interface) );

                    interface_td.appendChild( interface_td_text );

                    interface_tr.appendChild( interface_td_label );
                    interface_tr.appendChild( interface_td );

                    stateTable.appendChild( interface_tr );


                    for (i = 0; i < state.length; i++) {

                        var sess_id_tr = document.createElement("tr");

                        var sess_id_td_label = document.createElement("td");
                        var sess_id_td_label_text = document.createTextNode( "Session ID:" );

                        sess_id_td_label.appendChild( sess_id_td_label_text );

                        var sess_id_td = document.createElement("td");
                        var sess_id_td_text = document.createTextNode( state[i].id );

                        sess_id_td.appendChild( sess_id_td_text );

                        sess_id_tr.appendChild( sess_id_td_label );
                        sess_id_tr.appendChild( sess_id_td );

                        stateTable.appendChild( sess_id_tr );

                        var ips_tr = document.createElement("tr");

                        var source_ip_td_label = document.createElement("td");
                        var source_ip_td_label_text = document.createTextNode( "Source:" );

                        source_ip_td_label.appendChild( source_ip_td_label_text );

                        var source_td = document.createElement("td");

                        var source_string = state[i].source_ip.concat(":"+state[i].source_port);

                        var source_td_text = document.createTextNode( source_string );

                        source_td.appendChild( source_td_text );

                        ips_tr.appendChild( source_ip_td_label );
                        ips_tr.appendChild( source_td );


                        var dest_ip_td_label = document.createElement("td");
                        var dest_ip_td_label_text = document.createTextNode( "Destination:" );

                        dest_ip_td_label.appendChild( dest_ip_td_label_text );

                        var dest_td = document.createElement("td");

                        var dest_string = state[i].destination_ip.concat(":"+state[i].destination_port);

                        var dest_td_text = document.createTextNode( dest_string );

                        dest_td.appendChild( dest_td_text );

                        ips_tr.appendChild( dest_ip_td_label );
                        ips_tr.appendChild( dest_td );


                        stateTable.appendChild( ips_tr );


                        var app_tr = document.createElement("tr");

                        var app_td_label = document.createElement("td");
                        var app_td_label_text = document.createTextNode( "Application:" );

                        app_td_label.appendChild( app_td_label_text );

                        var app_td = document.createElement("td");
                        var app_td_text = document.createTextNode( state[i].app_name );

                        app_td.appendChild( app_td_text );

                        app_tr.appendChild( app_td_label );
                        app_tr.appendChild( app_td );

                        stateTable.appendChild( app_tr );




                    };

                });

            });
        },
        1000);




    </script>
    </body>
    </html>

    '''

app.run(debug=True, port=8000, host='0.0.0.0')
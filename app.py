#! /usr/bin/python

from lxml import etree
import xml.etree.ElementTree as ET
import flask
import time
import thread
import time

from flask import jsonify



from srx_wanmon_utils import if_fw_state_count, ifstats, routeFinder, if_fw_states, collectRPMStats, collectIPMStatus


from flask import jsonify

from jnpr.junos import Device


device_stats = {}


def collectSessCount (device):

    global device_stats

    device_stats["prime_if_fw_state_count"] = if_fw_state_count(device , "gr-0/0/0.0")

    device_stats["alt_if_fw_state_count"] = if_fw_state_count(device , "st0.0")


def gatherRPMStats (device):

    global device_stats

    device_stats["rpm_results"] = collectRPMStats(device)

    device_stats["ipm_status"] = collectIPMStatus(device)

# method to collect interface stats for a given device

def collectGRIfStats (device):

    # store the recorded results in the GLOBAL device_stats dictionary
    global device_stats

    gr_stat_dict = ifstats(device, "gr-0/0/0.0")

    device_stats["gr_if"] = gr_stat_dict


def collectSTIfStats (device):

    # store the recorded results in the GLOBAL device_stats dictionary
    global device_stats

    st_stat_dict = ifstats(device, "st0.0")

    device_stats["st_if"] = st_stat_dict


def collectRouteStats (device):

    global device_stats

    inet0_dict = routeFinder(device, "inet.0")

    device_stats["inet0"] = inet0_dict

    app_route_dict = routeFinder(device, "app-route-inet.inet.0")

    device_stats["approute"] = app_route_dict


def collectSessions (device):

    device_sessions = {}

    device_sessions["gr-0/0/0.0"] = if_fw_states (device, "gr-0/0/0.0")

    device_sessions["st0.0"] = if_fw_states(device, "st0.0")

    return  device_sessions


device_sessions = {}




def ifGRStatLoop (device):
    while True:
        collectGRIfStats(device)

        #time.sleep(1)

def ifSTStatLoop (device):
    while True:
        collectSTIfStats(device)

        #time.sleep(1)

def sessionLoop (device):

    global device_sessions

    while True:

        try:
            device_sessions = collectSessions (device)
        except:
            device.close()
            device.open()

        time.sleep(10)

def sessionCountLoop (device):

    while True:

        try:
            collectSessCount (device)
        except:
            device.close()
            device.open()

        time.sleep(10)

def rpmStatLoop (device):

    while True:

        gatherRPMStats(device)


def routeStatLoop (device):

    while True:
        collectRouteStats(device)


        time.sleep(5)



fast_dev = Device(host="10.164.0.243", user="root", password="Welcome!")

slow_dev = Device(host="10.164.0.243", user="root", password="Welcome!")


try:
    fast_dev.open()
except:
    print "Fast Connection Failed"
    exit()

try:
    slow_dev.open()
except:
    print "Slow Connection Failed"
    exit()




# Create a device connection for stat collection

try:

    # create a thread to collect interface stats from the device

    thread.start_new_thread(ifGRStatLoop, (fast_dev,))

except:

    print "Connection to device failed - GRE Interface Statistic Monitoring Failed."
    fast_dev.close()
    raise


try:

    # create a thread to collect interface stats from the device

    thread.start_new_thread(ifSTStatLoop, (fast_dev,))

except:

    print "Connection to device failed - IPSec Interface Statistic Monitoring Failed."
    fast_dev.close()
    raise

try:

    thread.start_new_thread(routeStatLoop, (fast_dev,))

except:
    print "Connection to device failed - Route Stat Monitoring Failed."
    fast_dev.close()
    raise

try:

    thread.start_new_thread(rpmStatLoop, (fast_dev,))

except:
    print "Connection to device failed - RPM Stat Monitoring Failed."
    fast_dev.close()
    raise

try:

    # create a thread to collect firewall sessions from the device

    thread.start_new_thread(sessionLoop, (slow_dev,))


except:

    print "Connection to device failed - Firewall Session Monitoring Failed."
    slow_dev.close()
    raise

try:

    # create a thread to collect firewall sessions from the device

    thread.start_new_thread(sessionCountLoop, (fast_dev,))


except:

    print "Connection to device failed - Firewall Session Counting Failed."
    slow_dev.close()
    raise






app = flask.Flask(__name__)


@app.route('/_get_sessions')
def get_sessions():
    return jsonify( device_sessions )


@app.route('/_get_statistics')
def get_statistics():
    return jsonify( ipm_status = device_stats["ipm_status"] , rpm_current_probes_percent_lost = device_stats["rpm_results"]["current_probes_percent_lost"] , rpm_current_probes_sent = device_stats["rpm_results"]["current_probes_sent"], rpm_last_probes_percent_lost = device_stats["rpm_results"]["last_probes_percent_lost"] , rpm_last_probes_sent = device_stats["rpm_results"]["last_probes_sent"] , rpm_current_probes_received = device_stats["rpm_results"]["current_probes_received"] , rpm_target_interface =  device_stats["rpm_results"]["target_interface"], rpm_last_probes_received = device_stats["rpm_results"]["last_probes_received"] , rpm_target_address = device_stats["rpm_results"]["target_address"] , alt_if_fw_state_count = device_stats["alt_if_fw_state_count"]["state_count"] , prime_if_fw_state_count = device_stats["prime_if_fw_state_count"]["state_count"], inet_table=device_stats["inet0"]["table"] , inet_route = device_stats["inet0"]["route"] , inet_route_nh = device_stats["inet0"]["nh_if"] , alt_table=device_stats["approute"]["table"] , alt_table_route = device_stats["approute"]["route"] , alt_table_nh = device_stats["approute"]["nh_if"] , gr_if_ibps = device_stats["gr_if"]["ibps"] , gr_if_ipps = device_stats["gr_if"]["ipps"] , gr_if_obps = device_stats["gr_if"]["obps"] , gr_if_opps =  device_stats["gr_if"]["opps"] , st_if_ibps = device_stats["st_if"]["ibps"] , st_if_ipps = device_stats["st_if"]["ipps"] , st_if_obps = device_stats["st_if"]["obps"] , st_if_opps = device_stats["st_if"]["opps"] )


@app.route('/')
def index():
    return '''
    <html>
    <head>
    <style>

    .outer_table {
        border-radius: 15px;
        border: 2px solid black;
        padding: 15px;
        width: 85%;

    }

    .title_label {
        padding:5px 0px 25px 0px;
        text-decoration: underline;
    }


    </style>

    <title> SD-WAN Stats </title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>

    </head>

    <body>


    <table class="outer_table">
    <tr>
    <td class="title_label">Network Traffic</td>
    </tr>

    <tr>
    <td><u>Primary Internet Routing Table: </u></td>
    <td><div id="inettable"></div></td>
    <td><u>Alternate Internet Routing Table:</u></td>
    <td><div id="alttable"></div></td>
    </tr>

    <tr>
    <td>Active Route: </td>
    <td><div id="inetroute"></div></td>
    <td>Active Route: </td>
    <td><div id="altroute"></div></td>
    </tr>

    <tr>
    <td>Via Interface: </td>
    <td><div id="inet_route_nh"></div></td>
    <td>Via Interface: </td>
    <td><div id="alt_route_nh"></div></td>
    </tr>

    <tr></tr>
    <tr></tr>

    <tr>

    <td>


    <tr>

    <td>In BPS: </td> <td> <div id="gr_if_ibps"></div> </td>
    <td>In BPS: </td> <td> <div id="st_if_ibps"></div> </td>

    </tr>

    <tr>

    <td>In PPS: </td> <td> <div id="gr_if_ipps"></div> </td>
    <td>In PPS: </td> <td> <div id="st_if_ipps"></div> </td>

    </tr>

    <tr>

    <td>Out BPS: </td> <td> <div id="gr_if_obps"></div> </td>
    <td>Out BPS: </td> <td> <div id="st_if_obps"></div> </td>
    </tr>

    <tr>
    <td>Out PPS: </td> <td> <div id="gr_if_opps"></div> </td>
    <td>Out PPS: </td> <td> <div id="st_if_opps"></div> </td>
    </tr>







    </tr>
    </table>

    <br>
    <br>

    <table class="outer_table">

    <tr> <td class="title_label"> WAN Performance Statistics </td> </tr>
    <tr>
    <td>Monitored IP Address:</td>
    <td><div id="rpm_target_address"></div></td>
    <td>Monitored Inteface:</td>
    <td><div id="rpm_target_interface"></div></td>
    </tr>

    <tr>

    <td>
    <table>
    <tr><td>Current Probe Results</td></tr>
    <tr><td>Probes Sent:</td><td><div id="rpm_current_probes_sent"></div></td></tr>
    <tr><td>Probes Received:</td><td><div id="rpm_current_probes_received"></div></td></tr>
    <tr><td>Percentage of Probes Lost:</td><td><div id="rpm_current_probes_percent_lost"></div></td></tr>
    </table>
    </td>


    <td>
    <table>
    <tr><td>Previous Probe Results</td></tr>
    <tr><td>Probes Sent:</td><td><div id="rpm_last_probes_sent"></div></td></tr>
    <tr><td>Probes Received:</td><td><div id="rpm_last_probes_received"></div></td></tr>
    <tr><td>Percentage of Probes Lost:</td><td><div id="rpm_last_probes_percent_lost"></div></td></tr>
    </table>
    </td>

    </tr>

    <tr>
    <td>Test Result:</td>
    <td><div id="ipm_status"></div></td>
    </tr>

    </table>

    <br>
    <br>
    <table class="outer_table">

    <tr>
    <td class="title_label"> Firewall State Table Entries </td>
    </tr>

    <tr>
    <td>Primary WAN Session Count</td>
    <td>Alternate WAN Session Count</td>
    </tr>
    <tr>
    <td><div id="prime_if_fw_state_count"></div</td>
    <td><div id="alt_if_fw_state_count"></div></td>
    </tr>

    <tr>
    <td>
    <table id="stateTable">
    </table>
    </td>
    </tr>
    </table>


    <br>
    <br>
    <br>




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

                    $("#rpm_target_address").text(data.rpm_target_address);
                    $("#rpm_target_interface").text(data.rpm_target_interface);

                    $("#rpm_current_probes_sent").text(data.rpm_current_probes_sent);
                    $("#rpm_current_probes_received").text(data.rpm_current_probes_received);
                    $("#rpm_current_probes_percent_lost").text(data.rpm_current_probes_percent_lost);

                    $("#rpm_last_probes_sent").text(data.rpm_last_probes_sent);
                    $("#rpm_last_probes_received").text(data.rpm_last_probes_received);
                    $("#rpm_last_probes_percent_lost").text(data.rpm_last_probes_percent_lost);
                    $("#ipm_status").text(data.ipm_status);





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
                //var title_tr = document.createElement("tr");
                //var title_td_label = document.createElement("td");
                //var title_td_label_text = document.createTextNode( "State Table Entries" );
                //title_td_label.appendChild( title_td_label_text );
                //stateTable.appendChild( title_td_label );
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


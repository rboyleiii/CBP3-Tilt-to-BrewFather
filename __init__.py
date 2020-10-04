# brewfather craftbeerpi3 plugin
# Log Tilt temperature and SG data from CraftBeerPi 3.0 to the brewfather app
# https://brewfather.app/
#
# Note this code is heavily based on the Thingspeak plugin by Atle Ravndal and forked from the work of mowbraym
# and I acknowledge their efforts have made the creation of this plugin possible
# with that said, I will heavily modify all further comments for readability and clarify
#
# 2020.10.04 - Inital fork, changing behavior to find and send all defined tilt sensors to BrewFather
#
# TODO
#	

from modules import cbpi
from thread import start_new_thread
import time
import logging
import requests
import datetime

DEBUG = False

# Parameters
#added _tilt to brewfather_id (brewfather_tilt_id) as other brewfather device might have other oids, I know stream is differernt than tilt for example
#added the same for comment
brewfather_tilt_comment = None
brewfather_tilt_id = None

#def log(s):
#    if DEBUG:
#        s = "brewfather: " + s
#        cbpi.app.logger.info(s)

def log(text):
	filename = "./logs/Tilt2BrewF.log"
	formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	with open(filename, "a") as file:
		file.write("%s,%s\n" % (formatted_time, text))
	
@cbpi.initalizer(order=9000)
def init(cbpi):
    cbpi.app.logger.info("brewfather plugin Initialize")
    log("Brewfather params")
    
    # the comment that goes along with each post (visible in the edit data screen)
    global brewfather_tilt_comment

    # the unique id value (the bit following id= in the "Cloud URL" in the setting screen
    global brewfather_tilt_id
    
    brewfather_tilt_comment = cbpi.get_config_parameter("brewfather_tilt_comment", None)
    log("Brewfather brewfather_tilt_comment %s" % brewfather_tilt_comment)
    brewfather_tilt_id = cbpi.get_config_parameter("brewfather_tilt_id", None)
    log("Brewfather brewfather_tilt_id %s" % brewfather_tilt_id)

    if brewfather_tilt_comment is None:
	log("Init brewfather config Comment")
	try:
# TODO: is param2 a default value?
	    cbpi.add_config_parameter("brewfather_tilt_comment", "", "text", "Brewfather comment")
	except:
	    cbpi.notify("Brewfather Error", "Unable to update Brewfather comment parameter", type="danger")
    if brewfather_tilt_id is None:
	log("Init brewfather config URL")
	try:
# TODO: is param2 a default value?
	    cbpi.add_config_parameter("brewfather_tilt_id", "", "text", "Brewfather id")
	except:
	    cbpi.notify("Brewfather Error", "Unable to update Brewfather id parameter", type="danger")

    log("Brewfather params ends")

    # interval=900 is 900 seconds, 15 minutes, same as the Tilt Android App logs.
    # if you try to reduce this, brewfather will throw "ignored" status back at you

@cbpi.backgroundtask(key="brewfather_task", interval=900)
def brewfather_background_task(api):
    log("brewfather background task")

    #RB3, 10-04-2020 added this to store all sensor data.
    TiltList = {}
    def addTiltValue(color, name, value):
        if color not in TiltList:
            TiltList[color]={}
        TiltList[color][name]=value

    if brewfather_tilt_id is None:
        return False

    now = datetime.datetime.now()
	
    #RB3, 10-04-2020 changed this section to not rely on sensor order, instead collect all sensors available and then send the data.
    for key, value in cbpi.cache.get("sensors").iteritems():
	log("key %s value.name %s value.instance.last_value %s" % (key, value.name, value.instance.last_value))
	if (value.type == "TiltHydrometer"):
	    if (value.instance.sensorType == "Temperature"):
		temp = value.instance.last_value
		# brewfather expects *F so only convert back if we use C
		if (cbpi.get_config_parameter("unit",None) == "C"):
		    temp = value.instance.last_value * 1.8 + 32
                addTiltValue(value.instance.color, "Temp",temp)
	    if (value.instance.sensorType == "Gravity"):
		addTiltValue(value.instance.color, "Gravity",value.instance.last_value)
		
    #RB3 send collected data
    for TiltColor in TiltList:
	now = datetime.datetime.now()
        payload = "{ "
        # generate timestamp in "Excel" format
        timepoint = now.toordinal() - 693594 + (60*60*now.hour + 60*now.minute + now.second)/float(24*60*60)
        payload += " \"Timepoint\": \"%s\",\r\n" % timepoint
        payload += " \"Color\": \"%s\",\r\n" % TiltColor 
        payload += " \"Beer\": \"\",\r\n"
        if "Temp" in TiltList[TiltColor]:
            payload += " \"Temp\": \"%s\",\r\n" % TiltList[TiltColor]["Temp"]
        if "Gravity" in TiltList[TiltColor]:
            payload += " \"SG\": \"%s\",\r\n" % TiltList[TiltColor]["Gravity"]
        payload += " \"Comment\": \"%s\" }" % cbpi.get_config_parameter("brewfather_tilt_comment", None)
	log("Payload %s" % payload)
	url = "http://log.brewfather.net/tilt"
	headers = {
	    'Content-Type': "application/json",
	    'Cache-Control': "no-cache"
	    }
	id = cbpi.get_config_parameter("brewfather_tilt_id", None)
	querystring = {"id":id}
	r = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        if r.status_code != 200:
            cbpi.notify("Tilt to BF Error", "Received unsuccessful response. Ensure API key is correct. HTTP Error Code: " + str(response.status_code), type="danger", timeout=None)

	log("Result %s" % r.text)
	
    log("brewfather done")

#!/usr/bin/python3

import time
import json
import subprocess as sp

try:
	with open("/etc/automagic-fan/config.json","r") as file:
		config=json.load(file)
	FAN_OFF_TEMP=config["FAN_OFF_TEMP"]
	FAN_MAX_TEMP=config["FAN_MAX_TEMP"]
	UPDATE_INTERVAL=config["UPDATE_INTERVAL"]
	MAX_PERF=config["MAX_PERF"]
	INV_PWM=config["INV_PWM"]
	THERMAL_ZONE=config["THERMAL_ZONE"]
except:
	print("error loading /etc/automagic-fan/config.json.\nPlease check your config file.\nProceeding with default settings.")
	FAN_OFF_TEMP=20
	FAN_MAX_TEMP=50
	UPDATE_INTERVAL=2
	MAX_PERF=0
	INVERSE_PWM=0
	THERMAL_ZONE=0

def read_type(thermal_zone = 0):
	with open(f"/sys/devices/virtual/thermal/thermal_zone{thermal_zone}/type","r") as file:
		result=file.read()
	return result

print("""Binding to thermal zone: {thermal_zone} Type: {zone_type}""".format(thermal_zone = THERMAL_ZONE, zone_type = read_type(THERMAL_ZONE)))

if MAX_PERF>0:
	print("Maximizing clock speeds with jetson_clocks ...")
	sp.call("jetson_clocks")

if INVERSE_PWM>0:
	print("Fan PWM logic MODE: [inversed]")
else:
	print("Fan PWM logic MODE: [normal]")	

def read_temp(thermal_zone = 0):
	with open(f"/sys/devices/virtual/thermal/thermal_zone{thermal_zone}/temp","r") as file:
		result=file.read()
	result=int(result)/1000
	return result

def fan_curve(temp, inversed = False):
	spd=255*(temp-FAN_OFF_TEMP)/(FAN_MAX_TEMP-FAN_OFF_TEMP)
	if inversed:
		return 255-int(min(max(0,spd),255))
	else:	
		return int(min(max(0,spd),255))

def set_speed(spd):
	with open("/sys/devices/pwm-fan/target_pwm","w") as file:
		file.write(f"{spd}")

print("Setup complete.\nRunning normally.")
while True:
	temp=read_temp(THERMAL_ZONE)
	spd=fan_curve(temp, (INVERSE_PWM > 0))
	out=set_speed(spd)
	time.sleep(UPDATE_INTERVAL)



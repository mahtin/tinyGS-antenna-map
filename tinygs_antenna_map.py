#!/usr/bin/env python3
"""
	TinyGS Antenna Map - a program to create a map of TingGS received packets for antenna tuning
	Martin J Levy - W6LHI/G8LHI - https://github.com/mahtin/tinyGS-antenna-map
	Copyright (C) 2021 @mahtin - https://github.com/mahtin/tinyGS-antenna-map/blob/main/LICENSE

	Uses (for now) the packet date from TinyGS website - however, could be built into that website
"""

import sys
import getopt

from packets import PacketFileProcessing
from polar_map import PolarAntennaMap

def read_user_id():
	""" read_user_id """

	try:
		with open('.user_id', 'r') as f:
			user_id = f.read().strip()
	except FileNotFoundError:
		user_id = None
	return user_id

def tinygs_antenna_map(args):
	""" tinygs_antenna_map provides all the command line processing """

	verbose = False
	refresh_data = False
	station_names = None
	user_id = None
	antennas = {}
	max_days = None
	antenna_arg = None
	timebar_flag = False
	output_flag = False

	usage = ('usage: tinygs_antenna_map '
			+ '[-v|--verbose] '
			+ '[-h|--help] '
			+ '[-r|--refresh] '
			+ '[[-s|--station] station[,station...]] '
			+ '[[-u|--user] user-id] '
			+ '[[-a|--antenna] degrees] '
			+ '[[-d|--days] days] '
			+ '[-t|--timebar]'
			+ '[-o|--output]'
			)

	try:
		opts, args = getopt.getopt(args, 'vhrs:u:a:d:to', ['verbose', 'help', 'refresh', 'station=', 'user=', 'antenna=', 'days=', 'timebar',  'output'])
	except getopt.GetoptError:
		sys.exit(usage)

	for opt, arg in opts:
		if opt in ('-v', '--verbose'):
			verbose = True
		elif opt in ('-h', '--help'):
			sys.exit(usage)
		elif opt in ('-r', '--refresh'):
			refresh_data = True
		elif opt in ('-s', '--station'):
			station_names = arg
		elif opt in ('-u', '--user'):
			user_id = arg
		elif opt in ('-a', '--antenna'):
			antenna_arg = arg
		elif opt in ('-d', '--days'):
			max_days = arg
		elif opt in ('-t', '--timebar'):
			timebar_flag = True
		elif opt in ('-o', '--output'):
			output_flag = True
		else:
			sys.exit(usage)

	if len(args) != 0:
		sys.exit(usage)

	if not user_id:
		user_id = read_user_id()

	try:
		if user_id:
			user_id = int(user_id)
		if user_id == '0':
			user_id = None
	except ValueError:
		sys.exit('%s: user-id provided is non numeric' % ('tinygs_antenna_map'))

	if antenna_arg:
		for antenna in antenna_arg.split(','):
			if '@' in antenna:
				antenna_direction, antenna_station_name = antenna.split('@', 1)
			else:
				antenna_direction = antenna
				antenna_station_name = None
			try:
				antenna_direction = float(antenna_direction)
			except ValueError:
				sys.exit('%s: antenna direction provided is non numeric' % ('tinygs_antenna_map'))
			antennas[antenna_station_name] = antenna_direction

	if max_days:
		try:
			max_days = int(max_days)
		except ValueError:
			sys.exit('%s: days provided is non numeric' % ('tinygs_antenna_map'))
		if max_days <= 0:
			sys.exit('%s: days provided is invalid number' % ('tinygs_antenna_map'))

	if user_id is None and (station_names is None or len(station_names) == 0):
		sys.exit('%s: No station or user-id provided' % ('tinygs_antenna_map'))

	pfp = PacketFileProcessing(verbose)
	if refresh_data:
		pfp.set_refresh(True)
	if user_id:
		pfp.add_userid(user_id)
	if station_names:
		for station_name in station_names.split(','):
			pfp.add_station(station_name)
	else:
		pfp.add_all_stations()

	station_names = pfp.list_stations()
	if len(station_names) == 0:
		sys.exit('%s: No stations found' % ('tinygs_antenna_map'))

	for station_name in antennas:
		if station_name is None:
			continue
		if station_name not in station_names:
			sys.exit('%s: Antenna direction station not found' % ('tinygs_antenna_map'))

	for station_name in station_names:
		pfp.process_packets(station_name)
		if verbose:
			pfp.print_packets(station_name)

	# Let the plot begin!
	plot = PolarAntennaMap(timebar_flag)
	for station_name in station_names:
		packets = pfp.get_packets(station_name)
		plot.add_packets(station_name, packets, max_days)
		if None in antennas:
			antenna_direction = antennas[None]
			plot.add_antenna(station_name, antenna_direction)
		if station_name in antennas:
			antenna_direction = antennas[station_name]
			plot.add_antenna(station_name, antenna_direction)

	if output_flag:
		plot.output(sys.stdout.buffer, 'png')
	else:
		plot.display()
	sys.exit(0)

def main(args=None):
	""" main """
	if args is None:
		args = sys.argv[1:]
	tinygs_antenna_map(args)

if __name__ == '__main__':
	main()

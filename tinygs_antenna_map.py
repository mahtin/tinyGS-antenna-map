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

def tinygs_antenna_map(args):
	""" tinygs_antenna_map provides all the command line processing """

	verbose = False
	refresh_data = False
	station_names = None
	user_id = None
	antenna_direction = None
	output_flag = False

	usage = ('usage: tinygs_antenna_map '
			+ '[-v|--verbose] '
			+ '[-h|--help] '
			+ '[-r|--refresh] '
			+ '[[-s|--station] station[,station...]] '
			+ '[[-u|--user] user-id] '
			+ '[[-a|--antenna] degrees] '
			+ '[-o|--output]'
			)

	try:
		opts, args = getopt.getopt(args, 'vhrs:u:a:o', ['verbose', 'help', 'refresh', 'station=', 'user=', 'antenna=', 'output'])
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
			antenna_direction = arg
		elif opt in ('-o', '--output'):
			output_flag = True
		else:
			sys.exit(usage)

	if len(args) != 0:
		sys.exit(usage)

	if not user_id:
		try:
			with open('.user_id', 'r') as f:
				user_id = f.read().strip()
		except FileNotFoundError:
			user_id = None

	if refresh_data:
		# refresh_data - XXX to do - use fetch.sh for now
		pass

	try:
		if user_id:
			user_id = int(user_id)
		if user_id == '0':
			user_id = None
	except ValueError:
		sys.exit('%s: user-id provided is non numeric' % ('tinygs_antenna_map'))

	if antenna_direction:
		try:
			antenna_direction = float(antenna_direction)
		except:
			sys.exit('%s: antenna_direction provided is non numeric' % ('tinygs_antenna_map'))

	if user_id is None and (station_names is None or len(station_names) == 0):
		sys.exit('%s: No station or user-id provided' % ('tinygs_antenna_map'))

	pfp = PacketFileProcessing(verbose)
	if user_id:
		pfp.add_userid(user_id)
	if station_names:
		for station_name in station_names.split(','):
			pfp.add_station(station_name)
	else:
		pfp.add_all_stations()

	if len(pfp.list_stations()) == 0:
			sys.exit('%s: No stations found' % ('tinygs_antenna_map'))

	for station_name in pfp.list_stations():
		pfp.process_packets(station_name)
		if verbose:
			pfp.print_packets(station_name)

	# Let the plot begin!
	plot = PolarAntennaMap()
	for station_name in pfp.list_stations():
		packets = pfp.get_packets(station_name)
		plot.add_packets(station_name, packets)
		if antenna_direction:
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

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

def tinygs_antenna_map(args):
	""" tinygs_antenna_map provides all the command line processing """

	verbose = False
	refresh_data = False
	station_names = None
	user_id = None
	output_flag = False

	usage = ('usage: tinygs_antenna_map '
			+ '[-v|--verbose] '
			+ '[-h|--help] '
			+ '[-r|--refresh] '
			+ '[-s|--station[,station...]] '
			+ '[-u|--user] user-id]'
			+ '[-o|--output]'
			)

	try:
		opts, args = getopt.getopt(args, 'vhrs:u:o', ['verbose', 'help', 'refresh', 'station=', 'user=', 'output'])
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
		except FileNotFoundError as e:
			#sys.exit('%s: %s' % ('tinygs_antenna_map', e))
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
		sys.exit(usage)

	pfp = PacketFileProcessing(user_id, verbose)
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
		for station_name in pfp.list_stations():
			#packets = pfp.get_packets(station_name)
			#for p in packets:
			#	pass
			pfp.print_packets(station_name)

	if output_flag:
		pfp.file_packets()
	else:
		pfp.plot_packets()
	sys.exit(0)

def main(args=None):
	""" main """
	if args is None:
		args = sys.argv[1:]
	tinygs_antenna_map(args)

if __name__ == '__main__':
	main()

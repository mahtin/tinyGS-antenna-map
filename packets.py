#!/usr/bin/env python3
"""
	Packet File Processing

	Martin J Levy - W6LHI/G8LHI - https://github.com/mahtin/tinyGS-antenna-map
	Copyright (C) 2021 @mahtin - https://github.com/mahtin/tinyGS-antenna-map/blob/main/LICENSE
"""

import os
import sys
import json
import datetime

from structures import AzEl, LongLat, Station, Packet
from satellite import Satellite
from polar_map import PolarAntennaMap

class PacketFileProcessing:
	""" PacketFileProcessing - read files and generate data """

	DATA_DIRECTORY = 'data'

	def __init__(self, user_id, verbose=False):
		""" PacketFileProcessing """

		self._user_id = user_id
		self._stations = {}
		self._sat = {}
		self._packets = {}
		self._verbose = verbose

	def add_station(self, station_name):
		""" add_station """

		self.add_all_stations(match=station_name)

	def add_all_stations(self, match=None):
		""" add_all_stations """

		with open(PacketFileProcessing.DATA_DIRECTORY + '/' + 'stations.json', 'r') as fd:
			j = json.load(fd)
			for s in j:
				station_name = str(s['name'])
				if match and station_name != match:
					continue
				lnglat = LongLat(float(s['location'][1]), float(s['location'][0]))
				# we don't use all the data from the json file
				self._add_station(station_name, lnglat)

	def _add_station(self, station_name, lnglat):
		""" _add_station """

		station = Station(station_name, lnglat)
		self._stations[station_name] = station
		self._sat[station_name] = Satellite()
		self._sat[station_name].set_observer(station.lnglat, station.elevation)
		if self._verbose:
			print('%s' % (station_name), file=sys.stderr)

	def list_stations(self):
		""" list_stations """

		return sorted(self._stations.keys())

	def process_packets(self, station_name):
		""" process_packets """

		uniq_packets = {}
		for root, dirs, files in os.walk(PacketFileProcessing.DATA_DIRECTORY + '/' + station_name):
			for filename in files:
				if filename[-5:] != '.json' :
					continue
				with open(PacketFileProcessing.DATA_DIRECTORY + '/' + station_name + '/' + filename, 'r') as fd:
					j = json.load(fd)
					if 'packets' not in j:
						continue
					p = self._read_packets(station_name, j['packets'])
					# the uniquiness comes from using ident at the index; hence removing data with the same ident and hence date/time stamp
					uniq_packets.update(p)
		self._packets[station_name] = uniq_packets

	def get_packets(self, station_name):
		""" get_packets """

		return self._packets[station_name]

	def print_packets(self, station_name):
		""" print_packets """

		uniq_packets = self._packets[station_name]
		for ident in sorted(uniq_packets, key=lambda v: (uniq_packets[v].dt)):
			packet = uniq_packets[ident]
			if self._verbose:
				if packet.parsed:
					print('%s\t%s\t%s\t%d:%s\t%-14s %5.1f ; %s' % (station_name, packet.ident, packet.dt.replace(microsecond=0).isoformat(), packet.norad, packet.satellite, packet.lnglat, packet.elevation, packet.azel), file=sys.stderr)
				else:
					print('%s\t%s\t%s\t%d:%s\t%-14s %5.1f ; %s CRC-ERROR' % (station_name, packet.ident, packet.dt.replace(microsecond=0).isoformat(), packet.norad, packet.satellite, packet.lnglat, packet.elevation, packet.azel), file=sys.stderr)
			if packet.parsed:
				print('%s: %s @ %s' % (station_name, packet.satellite, packet.azel))
			else:
				print('%s: %s @ %s CRC-ERROR' % (station_name, packet.satellite, packet.azel))
		if self._verbose:
			print('')

	def plot_packets(self):
		plot = PolarAntennaMap()
		for station_name in self._stations.keys():
			plot.add_packets(station_name, self._packets[station_name])
		plot.display()

	def _read_packets(self, station_name, packets):
		""" _read_packets """
		uniq_packets = {}
		for p in packets:
			ident = str(p['id'])
			if ident in uniq_packets:
				continue
			jt = float(p['serverTime'])
			dt = datetime.datetime.utcfromtimestamp(jt/1000.0)
			norad = int(p['norad'])
			satellite_name = str(p['satellite'])

			try:
				lnglat = LongLat(float(p['satPos']['lng']), float(p['satPos']['lat']))
				elevation = float(p['satPos']['alt'])
			except:
				lnglat = LongLat(0.0, 0.0)
				elevation = 0.0

			try:
				self._sat[station_name].set_satellite(satellite_name)
				self._sat[station_name].set_when(dt)
				_, _, azel = self._sat[station_name].get_where()
			except:
				# we don't know where the satellite is
				azel = AzEl(0,0)

			if azel.el <= 0:
				# below the horizon
				continue

			# the uniquiness comes from using ident at the index; hence removing data with the same ident and hence date/time stamp
			if 'parsed' in p:
				# fully parsed packet
				uniq_packets[ident] = Packet(ident, dt, norad, satellite_name, lnglat, elevation, azel, p['parsed'])
			else:
				# CRC ERROR
				uniq_packets[ident] = Packet(ident, dt, norad, satellite_name, lnglat, elevation, azel)
		return uniq_packets


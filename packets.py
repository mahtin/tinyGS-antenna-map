#!/usr/bin/env python3
"""
	Packet File Processing

	Martin J Levy - W6LHI/G8LHI - https://github.com/mahtin/tinyGS-antenna-map
	Copyright (C) 2021 @mahtin - https://github.com/mahtin/tinyGS-antenna-map/blob/main/LICENSE
"""

import os
import sys
import time
import json
import datetime

from structures import AzEl, LongLat, Station, Packet
from satellite import Satellite
from polar_map import PolarAntennaMap
from networking import Networking

class PacketFileProcessing:
	""" PacketFileProcessing - read files and generate data """

	DATA_DIRECTORY = 'data'

	def __init__(self, user_id=None, verbose=False):
		""" PacketFileProcessing """

		self._user_id = user_id
		self._stations = None
		self._my_stations = {}
		self._sat = {}
		self._packets = {}
		self._networking = Networking()
		self._verbose = verbose

	def add_station(self, station_name):
		""" add_station """

		self.add_all_stations(match=station_name)

	def add_all_stations(self, match=None):
		""" add_all_stations """

		if self._stations is None:
			self._fetch_stations_from_tinygs()
		if self._stations is None:
			sys.exit('No list of station to work with - exiting!')

		ranking = 0
		for station_name in self._stations:
			ranking += 1
			station = self._stations[station_name]
			if self._user_id and self._user_id != station.user_id:
				continue
			if match and station_name != match:
				continue

			# does data for the station exist
			if not os.path.isdir(PacketFileProcessing.DATA_DIRECTORY + '/' + station_name):
				os.mkdir(PacketFileProcessing.DATA_DIRECTORY + '/' + station_name)

				if self._verbose:
					print('%s: Station folder/directory created!' % (station_name), file=sys.stderr)
				# Fetch some more data - prime thet cache
				_ = self._fetch_packets_from_tinygs(station)

			self._my_stations[station.name] = station
			self._sat[station.name] = Satellite()
			self._sat[station.name].set_observer(station.lnglat, station.elevation)

			if self._verbose:
				print('%s: Station processed! (#%d out of %d)' % (station.name, ranking, len(self._stations)), file=sys.stderr)

	def list_stations(self):
		""" list_stations """

		return sorted(self._my_stations.keys())

	def process_packets(self, station_name):
		""" process_packets """

		uniq_packets = {}
		most_recent_mtime = 0
		for _, _, files in os.walk(PacketFileProcessing.DATA_DIRECTORY + '/' + station_name):
			for filename in files:
				if filename[-5:] != '.json' :
					continue
				packets_filename = PacketFileProcessing.DATA_DIRECTORY + '/' + station_name + '/' + filename
				try:
					with open(packets_filename, 'r', encoding='utf8') as fd:
						j = json.load(fd)
						if 'packets' not in j:
							continue
						p = self._read_packets(station_name, j['packets'])
						# the uniquiness comes from using ident at the index; hence removing data with the same ident and hence date/time stamp
						uniq_packets.update(p)

						s = os.fstat(fd.fileno())
						if s.st_mtime > most_recent_mtime:
							most_recent_mtime = s.st_mtime
				except IOError as e:
					print("%s: %s - CONTINUE ANYWAY" % (packets_filename, e), file=sys.stderr)

		if int(time.time() - most_recent_mtime) > 12*3600:
			# We need fresh data!
			station = self._stations[station_name]
			filenames = self._fetch_packets_from_tinygs(station)

			for filename in filenames:
				if filename[-5:] != '.json' :
					continue
				packets_filename = PacketFileProcessing.DATA_DIRECTORY + '/' + station_name + '/' + filename
				try:
					with open(packets_filename, 'r', encoding='utf8') as fd:
						j = json.load(fd)
						if 'packets' not in j:
							continue
						p = self._read_packets(station_name, j['packets'])
						# the uniquiness comes from using ident at the index; hence removing data with the same ident and hence date/time stamp
						uniq_packets.update(p)
				except IOError as e:
					print("%s: %s - CONTINUE ANYWAY" % (packets_filename, e), file=sys.stderr)

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
			else:
				if packet.parsed:
					print('%s: %s @ %s' % (station_name, packet.satellite, packet.azel))
				else:
					print('%s: %s @ %s CRC-ERROR' % (station_name, packet.satellite, packet.azel))

	def file_packets(self, fd=sys.stdout.buffer, file_format='png'):
		""" file_packets """

		plot = self._plot_packets()
		plot.output(fd, file_format)

	def plot_packets(self):
		""" plot_packets """
		plot = self._plot_packets()
		plot.display()

	def _plot_packets(self):
		""" _plot_packets """

		if len(self._my_stations) == 0:
			raise ValueError('Plot not available because no stations added')
		plot = PolarAntennaMap()
		for station_name in self._my_stations:
			plot.add_packets(station_name, self._packets[station_name])
		return plot

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

	def _fetch_stations_from_tinygs(self):
		""" fetch_stations_from_tinygs """

		# Make data directory if not present - or simply make it and ignore the error
		try:
			os.mkdir(PacketFileProcessing.DATA_DIRECTORY)
		except FileExistsError:
			pass

		stations_filename = PacketFileProcessing.DATA_DIRECTORY + '/' + 'stations.json'

		file_update = False

		try:
			s = os.stat(stations_filename)
		except FileNotFoundError:
			# Let's assume the file does not exist
			file_update = True

		if not file_update:
			if s.st_size == 0:
				# Zero length files are bad - lets update it
				file_update = True
			if int(time.time() - s.st_mtime) > 5*24*3600:
				# File is more than five days old - so lets not update it.
				file_update = True

		if file_update:
			# Grab a fresh copy from the web (yes - I said "the web")
			self._networking.stations(stations_filename)

		stations = {}
		try:
			with open(stations_filename, 'r', encoding='utf8') as fd:
				j = json.load(fd)
				for s in j:
					# we don't use all the data from the json file
					# we sanatize this data also - just in case (Oh, yes. Little Bobby Tables, we call him)
					station_name = str(s['name']).replace('/','_').replace('.','_').replace(':','_')
					user_id = int(s['userId'])
					lnglat = LongLat(float(s['location'][1]), float(s['location'][0]))
					stations[station_name] = Station(station_name, user_id, lnglat)
			# Success!
			self._stations = stations

		except IOError as e:
			print("%s: %s - CONTINUE ANYWAY" % (stations_filename, e), file=sys.stderr)

	def _fetch_packets_from_tinygs(self, station):
		""" fetch_packets_from_tinygs """

		now = datetime.datetime.utcnow()
		# Filenames on Windows can't have :'s (colons) so keep this simple!
		filename = now.strftime('%Y-%m-%dT%H-%M-00') + '.packets.json'
		packets_filename = PacketFileProcessing.DATA_DIRECTORY + '/' + station.name + '/' + filename
		self._networking.packets(packets_filename, station)

		# we return a list just in case one day we fetch many files
		return [filename]

	def _fetch_tle(self):
		""" fetch_tle """

		tle_filename = PacketFileProcessing.DATA_DIRECTORY + '/' + 'tinygs_supported.txt'
		self._networking.tle(tle_filename)


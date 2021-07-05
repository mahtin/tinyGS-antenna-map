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
from networking import Networking

class PacketFileProcessing:
	""" PacketFileProcessing - read files and generate data """

	DATA_DIRECTORY = 'data'

	REFRESH_TIME_PACKETS = 12*3600			# Every twelve hours for packets
	REFRESH_TIME_STATIONS = 5*24*3600		# Every five days for stations
	REFRESH_TIME_TLE = 2*24*3600			# Every two days for TLE data

	_tle_checked = False

	def __init__(self, verbose=False):
		""" PacketFileProcessing """

		self._user_id = None
		self._stations = None
		self._my_stations = {}
		self._sat = {}
		self._packets = {}
		self._networking = Networking()
		self._refresh = False
		self._verbose = verbose

	def set_refresh(self, refresh=True):
		""" set_refresh """

		self._refresh = refresh
	def add_userid(self, user_id=None):
		""" add_userid """

		self._user_id = user_id

	def add_station(self, station_name):
		""" add_station """

		self.add_all_stations(match=station_name)

	def add_all_stations(self, match=None):
		""" add_all_stations """

		if self._stations is None:
			self._fetch_stations_from_tinygs()
		if self._stations is None:
			sys.exit('No list of station to work with - exiting!')

		if not PacketFileProcessing._tle_checked:
			# This helps the Satellite() code know about current TLEs
			# The key point is to do this before we ever call Satellite()
			# This isn't the best place to do this; however, we will survive!
			self._fetch_tle()
			PacketFileProcessing._tle_checked = True

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

		# process existing files - as a side effect, find the newest file
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

		# check to see if we need to refresh the data files
		if self._refresh or int(time.time() - most_recent_mtime) > PacketFileProcessing.REFRESH_TIME_PACKETS:
			old_len = len(uniq_packets)
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
			if self._verbose:
				if len(uniq_packets) - old_len > 0:
					print('%s: Station refresh added %d packets' % (station.name, len(uniq_packets) - old_len), file=sys.stderr)

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
					print('%s\t%s\t%s\t%5d:%s\t%16s %5.1f ; %16s' % (station_name, packet.ident, packet.dt.replace(microsecond=0).isoformat(), packet.norad, packet.satellite, packet.lnglat, packet.elevation, packet.azel), file=sys.stderr)
				else:
					print('%s\t%s\t%s\t%5d:%s\t%16s %5.1f ; %16s CRC-ERROR' % (station_name, packet.ident, packet.dt.replace(microsecond=0).isoformat(), packet.norad, packet.satellite, packet.lnglat, packet.elevation, packet.azel), file=sys.stderr)
			else:
				if packet.parsed:
					print('%s: %s @ %s' % (station_name, packet.satellite, packet.azel))
				else:
					print('%s: %s @ %s CRC-ERROR' % (station_name, packet.satellite, packet.azel))

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

		if self._refresh or self._is_file_old(stations_filename, PacketFileProcessing.REFRESH_TIME_STATIONS):
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
		if self._refresh or self._is_file_old(tle_filename, PacketFileProcessing.REFRESH_TIME_TLE):
			# Grab a fresh copy from the web (yes - I said "the web")
			self._networking.tle(tle_filename)

	@classmethod
	def _is_file_old(cls, filename, age):
		""" is_file_old """

		try:
			s = os.stat(filename)
			if s.st_size == 0:
				# Zero length files are bad - lets update it
				return True
			if int(time.time() - s.st_mtime) > age:
				# File is more than N days old - so update it.
				return True

		except FileNotFoundError:
			# Let's assume the file does not exist
			return True

		# No need to update file
		return False


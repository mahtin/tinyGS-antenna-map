#!/usr/bin/env python3
"""
	Misc Structures
	Martin J Levy - W6LHI/G8LHI - https://github.com/mahtin/tinyGS-antenna-map
	Copyright (C) 2021 @mahtin - https://github.com/mahtin/tinyGS-antenna-map/blob/main/LICENSE

"""

class AzEl:
	""" Azimuth and Elevation - where the satellite is in the sky based on the observer """

	def __init__(self, az, el):
		self.az = float(az)
		self.el = float(el)

	def __str__(self):
		return '[%.2f,%.2f]' % (self.az, self.el)

class LongLat:
	""" Latitude and Longitude - where an observer (or satellite) is on the earth's surface """

	def __init__(self, lng, lat):
		self.lng = float(lng)
		self.lat = float(lat)

	def __str__(self):
		if self.lng < 0.0:
			lng = '%.2fW' % (-self.lng)
		else:
			lng = '%.2fE' % (self.lng)
		if self.lat < 0.0:
			lat = '%.2fS' % (-self.lat)
		else:
			lat = '%.2fN' % (self.lat)
		return '[%s,%s]' % (lng, lat)

class Station:
	""" Station - just enough to know about a station """

	def __init__(self, name, lnglat, elevation=0.0):
		self.name = str(name)
		self.lnglat = lnglat
		self.elevation = float(elevation)

	def __str__(self):
		return '%s@%s^%.2f' % (self.name, self.lnglat, self.elevation)

class Packet:
	""" Packet - what was received and maybe decoded """

	def __init__(self, ident, dt, norad, satellite, lnglat, elevation, azel, parsed=None):
		self.ident = ident
		self.dt = dt
		self.norad = int(norad)
		self.satellite = satellite
		self.lnglat = lnglat
		self.elevation = float(elevation)
		self.azel = azel
		self.parsed = parsed

	def __str__(self):
		return '%s:%s->%d:%s@%s^%.2f:%s' % (self.ident, self.dt, self.norad, self.satellite, self.lnglat, self.elevation, self.azel)

class TLE:
	""" Two-Line Element - the magic incantation that tells all about orbiting bodies """

	def __init__(self, norad, name, line1, line2):
		self.norad = int(norad)
		self.name = str(name)
		self.line1 = str(line1)
		self.line2 = str(line2)

	def __str(self):
		return '%d:%s: line1: %s line2: %s' % (self.norad, self.name, self.line1, self.line2)


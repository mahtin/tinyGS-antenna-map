#!/usr/bin/env python3
"""
	Satellite - a simple TLE process
	Martin J Levy - W6LHI/G8LHI - https://github.com/mahtin/tinyGS-antenna-map
	Copyright (C) 2021 @mahtin - https://github.com/mahtin/tinyGS-antenna-map/blob/main/LICENSE

	sat = Satellite()
	sat.set_observer(lnglat)
	sat.set_satellite(name)
	sat.set_when(datetime)
	lnglat, elevation, azel = sat.get_where()
"""

import sys
import math
import datetime

import ephem

from structures import AzEl, LongLat, TLE

DATA_DIRECTORY = 'data'

class Satellite:
	""" Satellite """

	# A built-in limited TLE table; becuase, we don't need much to prove this code works
	# Now read/updated in via data/tinygs_supported.txt file
	_tle = {
		'Norbi':  TLE(46494, 'NORBI',   '1 46494U 20068J   21144.94739324  .00000401  00000-0  33748-4 0  9990', '2 46494  97.6941  82.6325 0019244 152.8048 207.4187 15.03600696 35800'),
		'SDSat':  TLE(47721, 'SDSat',   '1 47721U 21015W   21151.96754213 -.00000070  00000-0  00000+0 0  9994', '2 47721  97.4597 226.4296 0011101 324.0519  36.0248 15.20833952 14076'),
		'FEES':   TLE(48082, 'FEES',    '1 48082U 21022AL  21152.01156273  .00002152  00000-0  14918-3 0  9991', '2 48082  97.5606  54.5896 0016358   4.3765 121.4198 15.06571919  9102'),
		'VR3X-A': TLE(47463, 'V-R3X 1', '1 47463U 21006BC  21152.43105396  .00001493  00000-0  91276-4 0  9991', '2 47463  97.4835 213.6021 0009976 169.2555 203.1124 15.11736076 19618'),
		'VR3X-B': TLE(47467, 'V-R3X 2', '1 47467U 21006BG  21152.43367193  .00001603  00000-0  97514-4 0  9994', '2 47467  97.4845 213.6260 0010123 167.3486 249.4588 15.11803691 19611'),
		'VR3X-C': TLE(47524, 'V-R3X 3', '1 47524U 21006DQ  21152.15684340  .00001614  00000-0  97959-4 0  9998', '2 47524  97.4853 213.3874 0010153 166.3430 219.7387 15.11879557 19579'),
	}
	_tle_updated = False
	_tle_filename = DATA_DIRECTORY + '/' + 'tinygs_supported.txt'

	def __init__(self):

		self._observer = None
		self._satellite_name = None

		self._tle_rec = None
		if not Satellite._tle_updated:
			self._read_tle()
			Satellite._tle_updated = True

	def set_observer(self, lnglat, elevation=0.0):
		""" observer """

		self._observer = ephem.Observer()
		self._observer.lon = self._degrees_to_radians(lnglat.lng)
		self._observer.lat = self._degrees_to_radians(lnglat.lat)
		self._observer.elevation = elevation
		self._observer.date = datetime.datetime.utcnow()

	def set_satellite(self, satellite_name):
		""" satellite """

		try:
			s = Satellite._tle[satellite_name]
		except:
			raise IndexError
		if not s:
			raise NotImplementedError
		self._satellite_name = satellite_name
		self._tle_rec = ephem.readtle(s.name, s.line1, s.line2)

	def set_when(self, dt=None):
		""" when """

		if not self._observer or not self._tle_rec:
			raise Exception

		if dt:
			self._observer.date = dt
		else:
			self._observer.date = datetime.datetime.utcnow()

	def get_where(self):
		""" where """

		if not self._observer or not self._tle_rec:
			raise Exception

		# finally caculate where the satellite compared to the observer (i.e Az/El)
		self._tle_rec.compute(self._observer)
		lnglat = LongLat(self._radians_to_degrees(self._tle_rec.sublong), self._radians_to_degrees(self._tle_rec.sublat))
		elevation = self._tle_rec.elevation
		azel = AzEl(self._radians_to_degrees(self._tle_rec.az), self._radians_to_degrees(self._tle_rec.alt))
		return [lnglat, elevation, azel]

	def _radians_to_degrees(self, d):
		""" I think in degress - even if computers think in radians """

		return d * (180/math.pi)

	def _degrees_to_radians(self, a):
		""" I think in degress - even if computers think in radians """

		return a / (180/math.pi)

	def _read_tle(self):
		""" read the TLE's in """

		try:
			# Saved away from https://api.tinygs.com/v1/tinygs_supported.txt
			with open(Satellite._tle_filename, 'r') as fd:
				n = 0
				l = ['', '', '']
				for line in fd.readlines():
					l[n] = line.strip()
					if n == 2:
						satellite_name = l[0]
						line1 = l[1]
						line2 = l[2]
						norad = str(line1[2:7])		# https://www.celestrak.com/NORAD/documentation/tle-fmt.php
						Satellite._tle[satellite_name] = TLE(norad, satellite_name, line1, line2)
					n = (n + 1) % 3

		except FileNotFoundError as e:
			print('%s: %s - WILL CONTINUE ANYWAY' % (Satellite._tle_filename, e), file=sys.stderr)


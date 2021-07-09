
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

import math
import datetime

import ephem

from structures import AzEl, LongLat, TLE

class Satellite:
	""" Satellite """

	DATA_DIRECTORY = 'data'

	# A built-in limited TLE table; becuase, we don't need much to prove this code works
	# Now read/updated in via data/tinygs_supported.txt file
	_tle = {
		'Norbi':           TLE(46494, 'Norbi',           '1 46494U 20068J   21171.56680050  .00001399  00000-0  10640-3 0  9991', '2 46494  97.6936 109.0948 0019440  70.2955 290.0369 15.03626854 39805'),
		'SDSat':           TLE(47721, 'SDSat',           '1 47721U 21015W   21171.44232657 -.00000070  00000-0  00000-0 0  9993', '2 47721  97.4612 245.7217 0009950 249.9352 110.0983 15.20920648 17037'),
		'FEES':            TLE(48082, 'FEES',            '1 48082U 21022AL  21171.58982329  .00001838  00000-0  12797-3 0  9996', '2 48082  97.5572  73.8040 0014403 294.8526 111.5169 15.06628133 12056'),
		'VR3X-A':          TLE(47463, 'VR3X-A',          '1 47463U 21006BC  21171.17162378  .00001487  00000-0  90754-4 0  9999', '2 47463  97.4822 231.9589 0011368 111.7153 308.1704 15.11779214 22446'),
		'VR3X-B':          TLE(47467, 'VR3X-B',          '1 47467U 21006BG  21169.45647111  .00001328  00000-0  81368-4 0  9999', '2 47467  97.4831 230.3020 0011218 115.2320  10.3032 15.11840336 22183'),
		'VR3X-C':          TLE(47524, 'VR3X-C',          '1 47524U 21006DQ  21170.89786253  .00001545  00000-0  93817-4 0  9997', '2 47524  97.4850 231.7526 0011347 109.4781 336.1547 15.11922803 22408'),
		'Sri Shakthi Sat': TLE(47716, 'Sri Shakthi Sat', '1 47716U 21015S   21171.20129100 -.00000070  00000-0  00000-0 0  9999', '2 47716  97.4536 245.4575 0009230 252.9165 107.1279 15.21538626 16909'),
	}
	_tle_updated = False
	_tle_filename = DATA_DIRECTORY + '/' + 'tinygs_supported.txt'

	def __init__(self):

		self._observer = None
		self._satellite_name = None
		self._tle_rec = None

		# Only read the tle file once
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
		except IndexError as e:
			raise IndexError from e
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

	@classmethod
	def _radians_to_degrees(cls, d):
		""" I think in degress - even if computers think in radians """

		return d * (180/math.pi)

	@classmethod
	def _degrees_to_radians(cls, a):
		""" I think in degress - even if computers think in radians """

		return a / (180/math.pi)

	@classmethod
	def _read_tle(cls):
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
						epoch = str(line1[18:32])
						if satellite_name in Satellite._tle:
							existing_epoch = str(Satellite._tle[satellite_name].line1[18:32])
						else:
							existing_epoch = '00000000000000'
						if epoch >= existing_epoch:
							# Update our saved/compiled-in copy of the TLE's
							Satellite._tle[satellite_name] = TLE(norad, satellite_name, line1, line2)
						else:
							# print('%s: %s < %s New epoch is not newer - WILL CONTINUE ANYWAY' % (satellite_name, existing_epoch, epoch), file=sys.stderr)
							pass
					n = (n + 1) % 3

		except FileNotFoundError as e:
			# print('%s: %s - WILL CONTINUE ANYWAY' % (Satellite._tle_filename, e), file=sys.stderr)
			pass


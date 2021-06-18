#!/usr/bin/env python3
"""
	Packet File Processing

	Martin J Levy - W6LHI/G8LHI - https://github.com/mahtin/tinyGS-antenna-map
	Copyright (C) 2021 @mahtin - https://github.com/mahtin/tinyGS-antenna-map/blob/main/LICENSE
"""

import sys
import random

import requests

class Networking:
	""" Networking - grab files/content from TinyGS API """

	_URL_API_STATIONS = 'https://api.tinygs.com/v1/stations'
	_URL_API_PACKETS = 'https://api.tinygs.com/v2/packets'
	_URL_API_TLE = 'https://api.tinygs.com/v1/tinygs_supported.txt'

	_USER_AGENTS = [
		'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36'
		'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
		'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36'
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36 Edg/91.0.864.48',
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15'
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
	]

	_HTTP_HEADERS = {
		'Origin': 'https://tinygs.com',
		'Host': 'api.tinygs.com',
		'Referer': 'https://tinygs.com/',
		'User-Agent': random.choice(_USER_AGENTS),
		'Accept': 'application/json, text/plain, */*',
		'Accept-Language': 'en-us'
	}

	def __init__(self, verbose=False):
		""" Networking """

		self._session = None
		self._verbose = verbose

	def __del__(self):
		""" __del__ """

		if self._session:
			self._session.close()
			self._session = None

	def stations(self, filename):
		""" stations """

		# the stations file (i.e. we don't know the staion)
		url = Networking._URL_API_STATIONS
		headers = headers=Networking._HTTP_HEADERS
		self._api_call(url, headers, filename)

	def packets(self, filename, station):
		""" packets """

		# the packets file
		url = Networking._URL_API_PACKETS + '?station=' + station.name + '@' + str(station.user_id)
		headers = Networking._HTTP_HEADERS.copy()
		headers['Referer'] = 'https://tinygs.com/station/' + station.name + '@' + str(station.user_id)
		self._api_call(url, headers, filename)

	def tle(self, filename):
		""" tle """

		# the tle file
		url = Networking._URL_API_TLE
		headers = Networking._HTTP_HEADERS
		self._api_call(url, headers, filename)

	def _api_call(self, url, headers, filename, station=None):
		""" _api_call """

		if self._verbose:
			print("%s: downloading from %s" % (filename, url), file=sys.stderr)

		if not self._session:
			self._session = requests.Session()

		try:
			r = self._session.get(url, headers=headers, allow_redirects=True)
			r.raise_for_status()
			try:
				# save away data - this is byte for byte from the web - no encoding needed
				with open(filename, 'wb') as fd:
					fd.write(r.content)
			except IOError as e:
				print("%s: %s - CONTINUE ANYWAY" % (filename, e), file=sys.stderr)
				return False
		except Exception as e:
			print("%s: %s - CONTINUE ANYWAY" % (url, e), file=sys.stderr)
			return False

		return True


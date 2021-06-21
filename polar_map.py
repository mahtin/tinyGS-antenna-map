#!/usr/local/bin/python
"""
	Polar Antenna Map

	Martin J Levy - W6LHI/G8LHI - https://github.com/mahtin/tinyGS-antenna-map
	Copyright (C) 2021 @mahtin - https://github.com/mahtin/tinyGS-antenna-map/blob/main/LICENSE
"""

import math
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors

class PolarAntennaMap:
	""" PolarAntennaMap """

	theta_scale = 22.5			# Azimuth
	radius_scale = 10.0			# Elevation

	dot_size = 1.0

	def __init__(self):
		""" PolarAntennaMap """

		self._stations = []
		self._packets = {}
		self._buckets = {}
		self._antenna_direction = {}
		self._processed = False
		self._fig = None
		self._axs = None
		self._cmap = None

	def add_packets(self, station_name, packets=None):
		""" add_packets """

		if station_name not in self._packets:
			self._stations.append(station_name)
			self._packets[station_name] = {}
			self._buckets[station_name] = {}

		if packets is None or len(packets) == 0:
			return

		for p in packets:
			packet = packets[p]
			if packet.ident in self._packets[station_name]:
				# seen already
				continue
			self._packets[station_name][packet.ident] = packet

			az_bucket = math.floor(packet.azel.az/PolarAntennaMap.theta_scale) * PolarAntennaMap.theta_scale
			el_bucket = math.floor(packet.azel.el/PolarAntennaMap.radius_scale) * PolarAntennaMap.radius_scale
			k = (az_bucket, el_bucket)

			if packet.parsed:
				# only add to bucket if it's a parsed packet
				try:
					self._buckets[station_name][k] += 1
				except KeyError:
					self._buckets[station_name][k] = 1

	def add_antenna(self, station_name, direction):
		""" add_antenna """

		self._antenna_direction[station_name] = float(direction)

	def display(self):
		""" display """

		if not self._processed:
			self._process()
			self._processed = True
		plt.show()

	def output(self, fd, file_format='png'):
		""" output """

		if not self._processed:
			self._process()
			self._processed = True
		plt.tight_layout()
		plt.savefig(fd, dpi=150, transparent=False, format=file_format)

	def _process(self):
		""" _process """

		# https://matplotlib.org/stable/gallery/style_sheets/style_sheets_reference.html
		plt.style.use('classic')

		# https://matplotlib.org/stable/gallery/color/colormap_reference.html
		self._cmap = plt.cm.OrRd

		# N plots needed
		self._fig, self._axs = plt.subplots(1, len(self._stations), sharex=False, sharey=False, subplot_kw=dict(projection='polar'))
		if len(self._stations) == 1:
			# Somewhere in the docs it says use squeeze - but that didn't work
			self._axs = [self._axs]

		n = 0
		for station_name in sorted(self._stations):
			n_packets = len(self._packets[station_name])
			v_max = 0
			for k in self._buckets[station_name]:
				if self._buckets[station_name][k] > v_max:
					v_max = self._buckets[station_name][k]

			self._plot(n, station_name, n_packets, v_max)
			n += 1

		# This seems wrong - but I'm sticking with it for now
		width_inches = 3
		height_inches = 5
		self._fig.set_size_inches(width_inches * len(self._stations), height_inches)

		# XXX - this slows down Matplotlib a lot - need to find out how to not use it!
		# https://github.com/matplotlib/matplotlib/issues/16550
		# https://matplotlib.org/stable/tutorials/intermediate/tight_layout_guide.html
		# using constrained_layout=True on subplots() above is even worse!
		# self._fig.tight_layout()

		title = ' '.join(sorted(self._stations))
		# self._fig.canvas.set_window_title(title)
		plt.get_current_fig_manager().set_window_title(title)

	def _plot(self, n, station_name, n_packets, v_max):
		""" _plot """

		# build the actual plot - background color shading
		theta = []
		bottom = []
		radii = []
		width = []
		shades = []

		for k in self._buckets[station_name]:
			az_bucket, el_bucket = k

			v = self._buckets[station_name][k]

			# angle
			theta.append(self._degrees_to_radians(az_bucket + PolarAntennaMap.theta_scale/2.0))
			width.append(self._degrees_to_radians(PolarAntennaMap.theta_scale))

			# radius (remember - it's reversed!)
			bottom.append(self._map_el(el_bucket))
			radii.append(-PolarAntennaMap.radius_scale)

			# color
			shades.append(self._cmap(v/v_max))

		self._axs[n].bar(theta, radii, bottom=bottom, width=width, color=shades, alpha=0.9, label=station_name, linewidth=0.25, zorder=1)

		# build the actual plot - packet dots
		theta = []
		radii = []
		shades = []

		for k in self._packets[station_name]:
			az = self._packets[station_name][k].azel.az
			el = self._packets[station_name][k].azel.el

			theta.append(self._degrees_to_radians(az))
			radii.append(self._map_el(el))
			if self._packets[station_name][k].parsed:
				shades.append('black')
			else:
				# Red dots for un-parsed packets
				shades.append('red')

		# Packet dots are black/red with no alpha
		self._axs[n].scatter(theta, radii, color=shades, alpha=0.5, label=station_name, linewidth=0.0, zorder=2)

		if station_name in self._antenna_direction:
			self._axs[n].arrow(self._degrees_to_radians(self._antenna_direction[station_name]), self._map_el(90), 0.0, 87, head_width=0.05, head_length=5, fill=False, length_includes_head=True, linewidth=1, color='blue', zorder=3)

		# all the misc stuff - for both 'bars'
		self._axs[n].set_theta_offset(self._degrees_to_radians(90))
		self._axs[n].set_theta_direction(-1)
		self._axs[n].set_thetagrids(
			(0.0, 22.5, 45.0, 67.5, 90.0, 112.5, 135.0, 157.5, 180.0, 202.5, 225.0, 247.5, 270.0, 292.5, 315.0, 337.5),
			('N', '', 'NE', '', 'E', '', 'SE', '', 'S', '', 'SW', '', 'W', '', 'NW', ''),
			fontsize='small')
		self._axs[n].set_rlim(bottom=0.0, top=90.0, emit=False, auto=False)
		self._axs[n].set_rgrids(
			(self._map_el(90), self._map_el(80), self._map_el(70), self._map_el(60), self._map_el(50), self._map_el(40), self._map_el(30), self._map_el(20), self._map_el(10), self._map_el(0)),
			('', '80', '', '60', '', '40', '', '20', '', ''),
			angle=90.0,
			fontsize='small')

		# self._axs[n].set_xlabel('Direction/Azimuth')	# XXX doesn't work for polar
		# self._axs[n].set_ylabel('Elevation')		# XXX doesn't work for polar

		title = '%s\n%d Total Packets' % (station_name, n_packets)
		self._axs[n].set_title(title, pad=24.0, fontdict={'fontsize':'medium'})

		v_min = 0
		if v_max == 0:
			v_max =  v_min + 1
		if (v_max - v_min) <= 10:
			ticks = range(v_min,v_max+1)
		else:
			if ((v_max - v_min) % 4) == 0:
				ticks = range(v_min,v_max+1, 4)
			else:
				ticks = [v_min, v_max]

		v_cmap = cm.ScalarMappable(norm=colors.Normalize(vmin=v_min, vmax=v_max), cmap=self._cmap)
		v_cmap.set_array([])	# Not needed in matplotlib version 3.4.2 (and above?); but safe to leave in
		cbar = plt.colorbar(v_cmap, ax=self._axs[n], orientation='horizontal', ticks=ticks)
		cbar.set_label('#Packets/Direction', fontdict={'fontsize':'medium'})

		# self._axs[n].tick_params(grid_color='gray', labelcolor='gray')
		# self._axs[n].legend(loc='lower right', bbox_to_anchor=(1.2, 0.94), prop={'size': 6})

	@classmethod
	def _degrees_to_radians(cls, angle):
		""" I think in degress - even if computers think in radians """
		return (math.pi / 180.0) * angle

	@classmethod
	def _map_el(cls, el):
		""" map elevation - need 90 at the center of the graph """
		return 90.0 - el



"""
	Polar Antenna Map

	Martin J Levy - W6LHI/G8LHI - https://github.com/mahtin/tinyGS-antenna-map
	Copyright (C) 2021 @mahtin - https://github.com/mahtin/tinyGS-antenna-map/blob/main/LICENSE
"""

import sys
import math
import datetime

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors

class PolarAntennaMap:
	""" PolarAntennaMap """

	theta_scale = 22.5			# Azimuth
	radius_scale = 10.0			# Elevation

	dot_size = 1.0

	def __init__(self, timebar_flag, style_flag=None):
		""" PolarAntennaMap """

		self._stations = []
		self._packets = {}
		self._buckets = {}
		self._antenna_direction = {}
		self._processed = False
		self._fig = None
		self._axs = None
		self._cmap = None
		self._timebar_flag = timebar_flag
		self._style_flag = style_flag

	def add_packets(self, station_name, packets=None, max_days=None):
		""" add_packets """

		now = datetime.datetime.utcnow()

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
			if max_days and (now - packet.dt) > datetime.timedelta(days=max_days):
				# too old
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
		if self._timebar_flag:
			self._fig, self._axs = plt.subplots(1+1, len(self._stations), sharex=False, sharey=False, subplot_kw=dict(projection='polar'))
			# needed for 1+1
			self._axs = self._axs[0]
		else:
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

			self._per_station_polar_plot(n, station_name, n_packets, v_max)
			n += 1

		if self._timebar_flag:
			self._per_day_bar_plot()

		# This seems wrong - but I'm sticking with it for now
		if self._timebar_flag:
			width_inches = 3
			height_inches = 8
		else:
			width_inches = 3
			height_inches = 5

		self._fig.set_size_inches(width_inches * len(self._stations), height_inches)

		# XXX - this slows down Matplotlib a lot - need to find out how to not use it!
		# https://github.com/matplotlib/matplotlib/issues/16550
		# https://matplotlib.org/stable/tutorials/intermediate/tight_layout_guide.html
		# using constrained_layout=True on subplots() above is even worse!
		self._fig.tight_layout()

		title = ' '.join(sorted(self._stations))
		# self._fig.canvas.set_window_title(title)
		plt.get_current_fig_manager().set_window_title(title)

	def _per_station_polar_plot(self, n, station_name, n_packets, v_max):
		""" _per_station_polar_plot """

		if not self._style_flag or 'B' in self._style_flag:
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

			try:
				self._axs[n].bar(theta, radii, bottom=bottom, width=width, color=shades, alpha=0.9, label=station_name, linewidth=0.25, zorder=1)
			except ValueError:
				print('%s: Station data error - no plot data!' % (station_name), file=sys.stderr)

		if not self._style_flag or 'D' in self._style_flag:
			# build the actual plot - packet dots
			theta = []
			radii = []
			shades = []
			sizes = []
			alphas = []

			for k in self._packets[station_name]:
				az = self._packets[station_name][k].azel.az
				el = self._packets[station_name][k].azel.el

				theta.append(self._degrees_to_radians(az))
				radii.append(self._map_el(el))
				if self._packets[station_name][k].parsed:
					shades.append('black')
					sizes.append(4.0)
					alphas.append(1.0)
				else:
					# Red dots for un-parsed packets
					shades.append('red')
					sizes.append(2.0)
					alphas.append(0.7)

			# Packet dots are black/red with no alpha
			if matplotlib.__version__ < '3.4':
				# This can be done by setting alpha value on colors ... a TODO
				alphas = None

			try:
				self._axs[n].scatter(theta, radii, color=shades, s=sizes, alpha=alphas, label=station_name, linewidth=0.0, zorder=2)
			except ValueError:
				print('%s: Station data error - no plot data!' % (station_name), file=sys.stderr)

		if station_name in self._antenna_direction:
			self._axs[n].arrow(self._degrees_to_radians(self._antenna_direction[station_name]), self._map_el(90), 0.0, 87, head_width=0.05, head_length=5, fill=False, length_includes_head=True, linewidth=1, color='blue', zorder=3)

		# all the misc stuff - for both 'bars'
		self._axs[n].set_theta_offset(self._degrees_to_radians(90))
		self._axs[n].set_theta_direction(-1)
		self._axs[n].set_rlim(bottom=0.0, top=90.0, emit=False, auto=False)

		if not self._style_flag or 'A' in self._style_flag:
			# Axis text and grid lines
			theta_angles = (0.0, 22.5, 45.0, 67.5, 90.0, 112.5, 135.0, 157.5, 180.0, 202.5, 225.0, 247.5, 270.0, 292.5, 315.0, 337.5)
			theta_labels = ('N', '', 'NE', '', 'E', '', 'SE', '', 'S', '', 'SW', '', 'W', '', 'NW', '')
			radius_angles = (self._map_el(90), self._map_el(80), self._map_el(70), self._map_el(60), self._map_el(50), self._map_el(40), self._map_el(30), self._map_el(20), self._map_el(10), self._map_el(0))
			radius_lables = ('', '80', '', '60', '', '40', '', '20', '', '')
		else:
			# No Axis text; but still draw grid lines - hence angles
			theta_angles = (0.0, 22.5, 45.0, 67.5, 90.0, 112.5, 135.0, 157.5, 180.0, 202.5, 225.0, 247.5, 270.0, 292.5, 315.0, 337.5)
			theta_labels = ()
			radius_angles = (self._map_el(90), self._map_el(80), self._map_el(70), self._map_el(60), self._map_el(50), self._map_el(40), self._map_el(30), self._map_el(20), self._map_el(10), self._map_el(0))
			radius_lables = ()

		self._axs[n].set_thetagrids(theta_angles, theta_labels, fontsize='small')
		self._axs[n].set_rgrids(radius_angles, radius_lables, angle=90.0, fontsize='small')

		# self._axs[n].set_xlabel('Direction/Azimuth')	# XXX doesn't work for polar
		# self._axs[n].set_ylabel('Elevation')		# XXX doesn't work for polar

		if not self._style_flag or 'T' in self._style_flag:
			title = '%s\n%d Total Packets' % (station_name, n_packets)
			self._axs[n].set_title(title, pad=24.0, fontdict={'fontsize':'medium'})

		if not self._style_flag or 'C' in self._style_flag:
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
			try:
				cbar = plt.colorbar(v_cmap, ax=self._axs[n], orientation='horizontal', ticks=ticks)
				cbar.set_label('#Packets/Direction', fontdict={'fontsize':'medium'})
			except ValueError:
				print('%s: Station data error - no plot data!' % (station_name), file=sys.stderr)

		# self._axs[n].tick_params(grid_color='gray', labelcolor='gray')
		# self._axs[n].legend(loc='lower right', bbox_to_anchor=(1.2, 0.94), prop={'size': 6})

	def _per_day_bar_plot(self):
		""" _per_day_bar_plot """

		ax = plt.subplot(2,1,2, label='packets per day')

		# find all the days we have data for
		hist = {}
		all_days = {}
		for station_name in self._stations:
			hist[station_name] = self._per_day_counts(station_name)
			for day in hist[station_name].keys():
				all_days[day] = True


		# find holes (i.e. missing days)
		day_last = None
		extra_all_days = {}
		for day in sorted(all_days):
			if not day_last:
				day_last = day

			delta = day - day_last
			if delta.days > 1:
				# add the missing days
				for ii in range(delta.days-1,0,-1):
					missing_day = day - datetime.timedelta(days=ii)
					extra_all_days[missing_day] = True
			day_last = day
		all_days.update(extra_all_days)

		# build x axis values
		ii = 1
		x_values = []
		for day in sorted(all_days):
			if day in extra_all_days:
				x_values.append(u'\u200c' * ii)			# unique value - but blank!
				ii += 1
			else:
				x_values.append(day.strftime('%m/%d'))

		# plot
		previous_y = {}
		v_max = len(self._stations)
		v = 0
		y_max = 0
		for station_name in sorted(self._stations):
			for not_parsed in [0, 1]:
				y_values = []
				bottom_values = []
				for day in sorted(all_days):
					if day in hist[station_name]:
						y_value = hist[station_name][day][not_parsed]
					else:
						y_value = 0
					if day in previous_y:
						b_value = previous_y[day]
						previous_y[day] += y_value
					else:
						b_value = 0
						previous_y[day] = y_value

					bottom_values.append(b_value)
					y_values.append(y_value)
					if (b_value + y_value) > y_max:
						y_max = b_value + y_value

				if not_parsed:
					# crc errors etc
					ax.bar(x_values, y_values, bottom=bottom_values, color = self._cmap((v+1)/(v_max+2)), label=station_name, hatch='/')
				else:
					# real packets
					ax.bar(x_values, y_values, bottom=bottom_values, color = self._cmap((v+1)/(v_max+2)), label=station_name)
			v += 1

		if len(x_values) % 2 == 0:
			ax.set_xticks(x_values[1::2])
			ax.set_xticklabels(x_values[1::2])
		else:
			ax.set_xticks(x_values[::2])
			ax.set_xticklabels(x_values[::2])

		for tick in ax.get_xticklabels():
			tick.set_rotation(-90)

		if (y_max % 2) != 0:
			ax.set_yticks([0, y_max])
			ax.set_yticklabels([0, y_max])
		else:
			ax.set_yticks([0, int(y_max/2), y_max])
			ax.set_yticklabels([0, int(y_max/2), y_max])

		# ax.margins(0.05)
		ax.set_xlabel('Date', fontdict={'fontsize':'medium'})
		ax.set_ylabel('#Packets', fontdict={'fontsize':'medium'})
		title = 'Packets per day (UTC)'
		ax.set_title(title, pad=24.0, fontdict={'fontsize':'medium'})

	def _per_day_counts(self, station_name):
		""" _per_day_counts """
		days = {}
		for k in self._packets[station_name]:
			packet = self._packets[station_name][k]
			# round down to date (i.e. drop time)
			# this is all done in UTC!
			dt = packet.dt.date()
			if dt in days:
				if packet.parsed:
					days[dt][0] += 1
				else:
					days[dt][1] += 1

			else:
				if packet.parsed:
					days[dt] = [1, 0]
				else:
					days[dt] = [0, 1]
		return days

	@classmethod
	def _degrees_to_radians(cls, angle):
		""" I think in degress - even if computers think in radians """
		return (math.pi / 180.0) * angle

	@classmethod
	def _map_el(cls, el):
		""" map elevation - need 90 at the center of the graph """
		return 90.0 - el


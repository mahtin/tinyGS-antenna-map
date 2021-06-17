# tinyGS-antenna-map
This is the antenna performance plotted from [tinyGS](https://tinygs.com) reception data. See their [repository](https://github.com/G4lile0/tinyGS).

![W6LHI 433Mhhz 2](/doc/images/W6LHI_433Mhz_2.png?raw=true "W6LHI 433Mhhz 2")

The plot provides Azimuth and Elevation information showing the places in the sky, based on the observer/station, where the most satellite reception happens.
Darker means more reception. Individual packets received are the black dots. CRC Errors are shown as red dots.
The center of the circle is exactly vertical from the observer/station.
The edge of the circle is the horizon (well, kinda!).

For example, if you had just a simple horizontal dipole, then you would see a bias in the data towards the higher reception direction (90 degrees to the dipole).
If you have a tracking antenna then you should see a very spread out reception.

The program will display on the desktop if it is run in that environment.
If you want a CLI process, then look at the `-o` flag below.
The program uses `Matplotlib` and the INSTALL instructions are included.
Any problems? - please use GitHub issues.

## Install

Please read [INSTALL](/INSTALL.md) page and return here aftet finished.

## Setting up your user-id

To plot your own graphs from your own stations, you need to know what your own user-id on TinyGS is.
The first option is to save it away in a file for all the code to use.

### Storing your user-id

Use your Telegram **TinyGS Personal Bot** channel to find your user-id.
It's the passwordless login link you get with the `/weblogin` command.

![user-id](/doc/images/telegram-tinygs-personal-bot-weblogin.png?raw=true "user-id")

The user-id is the URL provided (see example image).
Use it to create a `.user_id` file via the following command:

```bash
$ echo '20000009' > .user_id
$
```

Your number will be different.

### Specifying user for each run

If you choose, you specify your user-id manually on each command below.

## Plotting your antenna map

All your stations will be plotted on a single page. Make the displayed page larger if you need.

```bash
$ ./tinygs_antenna_map.py
```

This assumes that you are on a machine with a display. If you are headless, then the following will be useful:

```bash
$ ./tinygs_antenna_map.py -o > pretty-graph.png
$ scp pretty-graph.png somewhere-else.example.com:
```

This isn't a perfect method; but works for today.

### tinygs_antenna_map.py options

The `tinygs_antenna_map.py` program takes various arguments.

```bash
tinygs_antenna_map [-v|--verbose] [-h|--help] [-r|--refresh] [-s|--station[,station...]] [-u|--user] user-id]

```

 * [-v|--verbose] - provide some information on each of the packets being processed/displayed.
 * [-h|--help] - this message.
 * [-r|--refresh] - presently unused; but will pull data from TinyGS site on demant.
 * [-s|--station[,station...]] - list the station or stations to plot. Use comma-seperated (i.e. A,B,C) for more than one station.
 * [-u|--user] user-id] - define the user-id vs using the `.user_id` file.
 * [-o|--output] - produce a PNG file on stdout (use: `tinygs_antenna_map.py -o > diagram.png` for example`).

### Specifing the station or user-id

To produce a plot for a specific user (for example `20000009`):

```bash
$ ./tinygs_antenna_map.py -u 20000009
```

Your number will be different.

To produce a plot for one of your specific stations, use the station name:

```bash
$ ./tinygs_antenna_map.py -s W6LHI_433Mhz
```

To produce a plot for someone else station (and I'm not judging you in anyway):

```bash
$ ./tinygs_antenna_map.py -s MALAONE -u 0
```

(No idea who `MALAONE` is). Note the `-u 0` argument. This overtides your `.user_id` file (as this is a different user).

## Optional TLE data from tinyGS

Should there be more satellites than are build into `satellite.py` file, then the following could help:

```
$ curl -sSLR https://api.tinygs.com/v1/tinygs_supported.txt > data/tinygs_supported.txt
$
```

In fact, this file should be updated semi-often as the TLE's for the satellite do change over time. The code will still work if this file is missing.


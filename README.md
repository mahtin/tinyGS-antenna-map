# tinyGS-antenna-map
This is the antenna performance plotted from [tinyGS](https://tinygs.com) reception data. See their [repository](https://github.com/G4lile0/tinyGS).

![W6LHI 433Mhhz 2](/doc/images/W6LHI_433Mhz_2.png?raw=true "W6LHI 433Mhhz 2")

## Install

The package is written in Python and requires some additional packages.
```bash
$ pip3 install -U `cat requirements`
...
$
```

if you see the following error ...
```
RuntimeError: module compiled against API version 0xe but this version of numpy is 0xd
```
... it's a case of `Matplotlib` and `numby` being out of sync. Make sure both are updated via the `pip3` command above.
See https://github.com/numpy/numpy/issues/655 & https://github.com/matplotlib/matplotlib/issues/10135 & https://stackoverflow.com/questions/48054531/runtimeerror-module-compiled-against-api-version-0xc-but-this-version-of-numpy etc etc.

## Executable

Also make the `tinygs_antenna_map.py` file executable.
```bash
$ chmod +x tinygs_antenna_map.py
```

## Setting up your user-id

To plot your own graphs from your own stations, you need to know what your own user-id on TinyGS is.
The first option is to save it away in a file for all the code to use.

### Storing  your user-id

Use your Telegram **TinyGS Personal Bot** channel to find your user-id. It's the passwordless login link you get with the `/weblogin` command.

![user-id](/doc/images/telegram-tinygs-personal-bot-weblogin.png?raw=true "user-id")

The user-id is the URL provided (see example image). Use it to create a `.user_id` file via the following command:
```bash
$ echo '20000009' > .user_id
$
```
Your number will be different.

### Specifying user for each run

If you choose, you specify your user-id manually on each command below.

## Fetching data from tinyGS

**NOTE** If you run this script often you will get banned from tinyGS website. It's not meant to be run more than once a day (or less).
```bash
$ ./fetch.sh
...
$
```
This will create a `data` directory and start populating it with station packet data.

If you wish to manually specify your user-id (or plot a different user-id), then do the following:
```bash
$ ./fetch.sh 20000009
...
$
```
Your number will be different.

## Plotting your antenna map

All your stations will be plotted on a single page. Make the displayed page larger if you need.
```bash
$ ./tinygs_antenna_map.py
```

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

## Optional TLE data from tinyGS

Should there be more satellites than are build into `satellite.py` file, then the following could help:
```
$ curl -sSLR https://api.tinygs.com/v1/tinygs_supported.txt > data/tinygs_supported.txt
$
```
In fact, this file should be updated semi-often as the TLE's for the satellite do change over time. The code will still work if this file is missing.


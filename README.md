# tinyGS-antenna-map
This is the antenna performance plotted from [tinyGS](https://tinygs.com) reception data. See their [repository](https://github.com/G4lile0/tinyGS).

![W6LHI 433Mhhz 2](/doc/images/W6LHI_433Mhz_2.png?raw=true "W6LHI 433Mhhz 2")

## Install

### The basics - setting up Python in a Raspberry Pi (or similar)

This code is Python3 and the following system cleanup would be useful for many other systems/programs. This confirms that only Python3 is installed and that it's cleanly running!

``` bash

$ sudo apt-get update
...
$
$ sudo apt-get install -y python3-pip
...
$ sudo apt-get remove -y python2
...
$ sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10
...
$
```

### Installing Matplotlib

After a hunk of testing, I've decied that using the system packages for `Matplotlib` (this will include `numpy`) is the best way to go.

```bash
$ sudo apt-get install -y python3-matplotlib
...
$
```

You can check which version you are running via:

```bash
$ dpkg-query -l python3-matplotlib python3-numpy
..
ii  python3-matplotlib 3.0.2-2      armhf        Python based plotting system in a style similar to Matlab (Python 3)
ii  python3-numpy      1:1.16.2-1   armhf        Fast array facility to the Python 3 language

$
```
or
```
$ python3 -c 'import matplotlib,numpy;print(matplotlib.__version__);print(numpy.__version__)'
3.0.2
1.16.2
$
```

### Installing additional items

Additionally, you will need the [jq](https://stedolan.github.io/jq/download/) command plus `git` commands.

```bash
$ sudo apt-get install jq
$ sudo apt-get install -y jq git
...
$
```

As the program is written in Python, it requires some additional Python packages/libaries to be installed before running anything.

```bash
$ sudo python3 -m pip install -U -r requirements.txt
...
$
```

### Special notes on Matplotlib

**This section is not normally needed; but provided for users that want newer libaries**

The `Matplotlib` library reqires the somewhat-matching `numpy` library.
On a Raspberry Pi (and maybe other systems) it's best to install these packages via system commands (vs `pip3`).
However, you can upgrade them to the latest code (if you really desire) using  these commands:

```bash
$ sudo apt install -y python3-numpy libopenjp2-7-dev libtiff5 libatlas-base-dev
...
$ sudo python3 -m pip install -U matplotlib numpy
...
$
```

There's plenty of issues with this method of install. More can be found via [numpy issue 14772](https://github.com/numpy/numpy/issues/14772) and [stackoverflow's vast collection of answers](https://stackoverflow.com/questions/48012582/pillow-libopenjp2-so-7-cannot-open-shared-object-file-no-such-file-or-directo).

if you see the following error ...
```
RuntimeError: module compiled against API version 0xe but this version of numpy is 0xd
```
... it's a case of `Matplotlib` and `numby` being out of sync. Make sure both are updated via the `pip3` command above.
See [numpy issue 655](https://github.com/numpy/numpy/issues/655) and [matplotlib issue 10135](https://github.com/matplotlib/matplotlib/issues/10135) and [yet another stackpath answer]( https://stackoverflow.com/questions/48054531/runtimeerror-module-compiled-against-api-version-0xc-but-this-version-of-numpy) etc etc.

## Executable

Also make the `fetch.sh` and  `tinygs_antenna_map.py` file executable.
```bash
$ chmod +x fetch.sh tinygs_antenna_map.py
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

## Optional TLE data from tinyGS

Should there be more satellites than are build into `satellite.py` file, then the following could help:
```
$ curl -sSLR https://api.tinygs.com/v1/tinygs_supported.txt > data/tinygs_supported.txt
$
```
In fact, this file should be updated semi-often as the TLE's for the satellite do change over time. The code will still work if this file is missing.


# tinyGS-antenna-map
This is the antenna performance plotted from [tinyGS](https://tinygs.com) reception data. See their [repository](https://github.com/G4lile0/tinyGS).

![W6LHI 433Mhhz 2](/doc/images/W6LHI_433Mhz_2.png?raw=true "W6LHI 433Mhhz 2")

## Install

The package is written in Python and requires some additional packages.
```
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
```
$ chmod +x tinygs_antenna_map.py
```

## Setting up a user id file

Use your Telegram *TinyGS Personal Bot* channel to find your user id. It's the passwordless login link you get with the `/weblogin` command.

![user id](/doc/images/telegram-tinygs-personal-bot-weblogin.png?raw=true "user id")

The user id is the URL provided (see example image). Use it to create a `.user_id` file via the following command:
```
$ echo '20000009' > .user_id
$
```
Your number will be different.

## Fetching data from tinyGS

*NOTE* If you run this script often you will get banned from tinyGS website. It's not meant to be run more than once a day (or less).
```
$ ./fetch.sh
...
$
```
This will create a `data` directory and start populating it with station packet data.

## Plotting your antenna map

All your stations will be plotted on a single page. Make the displayed page larger if you need.
```
$ ./tinygs_antenna_map.py
```

## Optional TLE data from tinyGS

Should there be more satellites than are build into `satellite.py` file, then the following could help:
```
$ curl -sSLR https://api.tinygs.com/v1/tinygs_supported.txt > data/tinygs_supported.txt
$
```
In fact, this file should be updated semi-often as the TLE's for the satellite do change over time. The code will continue if this file is missing.


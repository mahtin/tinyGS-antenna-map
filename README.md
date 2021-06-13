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

Also make the `tinygs_antenna_map.py` file executable.
```
$ chmod +x tinygs_antenna_map.py
```

## Setting up a user id file

Use the Telegram channel passwordless login link to find your user id then create a user id file.
```
$ echo '99999999' > .user_id
$
```

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


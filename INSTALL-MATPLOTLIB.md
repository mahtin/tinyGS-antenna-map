# tinyGS-antenna-map
This is the antenna performance plotted from [tinyGS](https://tinygs.com) reception data. See their [repository](https://github.com/G4lile0/tinyGS).

## Install

Having a good Python 3 setup is vital. Getting a good `Matplotlib` setup is tricky, but doable.

### The basics - setting up Python 3 in a Raspberry Pi (or similar)

This code is Python 3 and the following system cleanup would be useful for many other systems/programs. This confirms that only Python 3 is installed and that it's cleanly running!

``` bash

$ sudo apt-get update
...
$ sudo apt-get install -y python3-pip
...
$ sudo apt-get remove -y python2
...
$ sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10
...
$
```

### Installing Matplotlib

After a hunk of testing, I've decided that using the system packages for `Matplotlib` (this will include `numpy`) is the best way to go.

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

### Special notes on Matplotlib

**This section is not normally needed; but provided for users that want newer libraries**

The `Matplotlib` library requires the somewhat-matching `numpy` library.
On a Raspberry Pi (and maybe other systems) it's best to install these packages via system commands (vs `pip3`).
However, you can upgrade them to the latest code (if you really desire) using these commands:

```bash
$ sudo apt install -y python3-numpy libopenjp2-7-dev libtiff5 libatlas-base-dev
...
$ sudo python3 -m pip install -U matplotlib numpy
...
$
```

There's plenty of issues with this method of installation. More can be found via [numpy issue 14772](https://github.com/numpy/numpy/issues/14772) and [stackoverflow's vast collection of answers](https://stackoverflow.com/questions/48012582/pillow-libopenjp2-so-7-cannot-open-shared-object-file-no-such-file-or-directo).

if you see the following error ...
```
RuntimeError: module compiled against API version 0xe but this version of numpy is 0xd
```
... it's a case of `Matplotlib` and `numby` being out of sync. Make sure both are updated via the `pip3` command above.
See [numpy issue 655](https://github.com/numpy/numpy/issues/655) and [matplotlib issue 10135](https://github.com/matplotlib/matplotlib/issues/10135) and [yet another stackpath answer]( https://stackoverflow.com/questions/48054531/runtimeerror-module-compiled-against-api-version-0xc-but-this-version-of-numpy) etc etc.

## Next steps

Please return to the [README](/README.md) file.

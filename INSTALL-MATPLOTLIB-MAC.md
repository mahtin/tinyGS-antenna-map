# tinyGS-antenna-map
This is the antenna performance plotted from [tinyGS](https://tinygs.com) reception data. See their [repository](https://github.com/G4lile0/tinyGS).

## Install part one - the background stuff

On a fresh Mac, it's recommended that you update `pip3` and setup a Python environment for yourself (via the `--user` option to `pip3`).
Some of these fixes are needed on an out-of-the-box Mac for any `python3` work.

```bash
$ python3 -m pip install --user --upgrade pip
...
$ export PATH=$HOME/Library/Python/3.8/bin:$PATH
$ echo 'export PATH=$HOME/Library/Python/3.8/bin:$PATH' >> $HOME/.profile
```

After this, the `pip3` command will be freshly-installed and updated and available to use. Test this step via:

```bash
$ which pip3
/Users/whomever/Library/Python/3.8/bin/pip3
$ pip3 -V
pip 21.1.3 from /Users/whomever/Library/Python/3.8/lib/python/site-packages/pip (python 3.8)
$
```

The `$PATH` update above is important, you won't be able to delete or move what's in `/usr/bin` so updating the $PATH` variable is vital!

## Install part two - the program specific important part

### Cython

The `Cython` install is needed; but does not exists in the `requirements.txt` file for portability reasons.
Hence the need for this command before any install is started.

```bash
$ pip3 install --user Cython
...
$
```

## Install part three - optionally install Matplotlib and Numpy

Once done, a quite-boring install of the Matplotlib can be done either manually via this:

```
$ pip3 install --user 'numpy>=1.16.2' 'matplotlib>=3.0.2'
...
$
```

Or you can simply let that happen as part of the `requirements.txt` process back on the main `README` page.

## Next steps

Please return to the [README](/README.md) file.


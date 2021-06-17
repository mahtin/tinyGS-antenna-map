## Fetching data from tinyGS

This is removed - not needed anymore.

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

## The jq program

Additionally, you will need the [jq](https://stedolan.github.io/jq/download/) command to get `fetch.sh` to work.

```bash
$ sudo apt-get install -y jq
...
$
```


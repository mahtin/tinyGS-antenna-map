:

# Martin J Levy - W6LHI/G8LHI - https://github.com/mahtin/tinyGS-antenna-map
# Copyright (C) 2021 @mahtin - https://github.com/mahtin/tinyGS-antenna-map/blob/main/LICENSE

# Fetch latest packet data from TinyGS - with stations based on the user id stored in .user_id file
# If you have added more stations - then delete the cached data/stations.json file
#

if [ "$#" -eq 1 ]
then
	USER_ID=$1
else

	if [ ! -s .user_id ]
	then
		echo "$0: Create a .user_id file which contains your tinyGS user id - see README file on GitHub" 1>&2
		exit 1
	fi

	USER_ID="`cat .user_id`"
fi

DATE=`date -u +%Y-%m-%dT%H:%M:00`		# Everything is UTC - it's always UTC

SILENT='sS'					# Change to "" if you want some friendly debug

DATA='data'

mkdir -p ${DATA} 2>/dev/null

if [ "`which jq`" == "" ]
then
	echo "$0: Install jq command - see README file on GitHub" 1>&2
	exit 1
fi

if [ ! -s ${DATA}/stations.json ]
then
	# Grab a fresh stations list
	curl -${SILENT}LR \
		-H 'Origin: https://tinygs.com' \
		-H 'Host: api.tinygs.com' \
		-H "Referer: https://tinygs.com/" \
		-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15' \
		-H 'Accept: application/json, text/plain, */*' \
		-H 'Accept-Language: en-us' \
			"https://api.tinygs.com/v1/stations" |\
		jq . > ${DATA}/stations.json
fi

STATION_LIST=`jq -cr '.[]|.name,.userId' < ${DATA}/stations.json | paste - - | awk '$2 == "'${USER_ID}'" { print $1; }' | sort`

if [ -z "${STATION_LIST}" ]
then
	echo "$0: No station found for provided user id" 1>&2
	exit
fi

for station in ${STATION_LIST}
do
	echo "Station: ${station}" 1>&2
	mkdir -p ${DATA}/${station} 2>/dev/null

	curl -${SILENT}LR \
		-H 'Origin: https://tinygs.com' \
		-H 'Host: api.tinygs.com' \
		-H "Referer: https://tinygs.com/station/${station}@${USER_ID}" \
		-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15' \
		-H 'Accept: application/json, text/plain, */*' \
		-H 'Accept-Language: en-us' \
			"https://api.tinygs.com/v2/packets?station=${station}@${USER_ID}" |\
	jq . | tee ${DATA}/${station}/${DATE}.packets.json | jq -cr '.packets[]|.serverTime,.satPos.lat,.satPos.lng' | paste - - - 

	# be kind
	sleep 1
done

exit 0

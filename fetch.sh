:

# Martin J Levy - W6LHI/G8LHI - https://github.com/mahtin/tinyGS-antenna-map
# Copyright (C) 2021 @mahtin - https://github.com/mahtin/tinyGS-antenna-map/blob/main/LICENSE

# Fetch latest packet data from TinyGS - with stations based on the user id stored in .user_id file
# If you have added more stations - then delete the cached data/stations.json file
#

if [ ! -s .user_id ]
then
	echo "$0: Create a .user_id file which contains your tinyGS user id - which can be found via passwordless login link in telegram channel" 1>&2
	exit 1
fi

USER_ID="`cat .user_id`"

DATE=`date -u +%Y-%m-%dT%H:%M:00`		# Everything is UTC - it's always UTC

SILENT='sS'					# Change to "" if you want some friendly debug

DATA='data'

if [ ! -d ${DATA} ]
then
	mkdir ${DATA}
fi

if [ ! -s ${DATA}/stations.json ]
then
	# Grab a fresh stations list
	curl -${SILENT}LR \
		-H 'Origin: https://tinygs.com' \
		-H 'Host: api.tinygs.com' \
		-H "Referer: https://tinygs.com/user/${USER_ID}" \
		-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15' \
		-H 'Accept: application/json, text/plain, */*' \
		-H 'Accept-Language: en-us' \
			"https://api.tinygs.com/v1/stations?userId=${USER_ID}" |\
		jq . | tee ${DATA}/stations.json | jq -cr '.[]|.name'
fi

STATION_LIST=`jq -cr '.[]|.name' < ${DATA}/stations.json | sort`

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

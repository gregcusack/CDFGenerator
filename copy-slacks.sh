#!/bin/bash

namespace=$1
workload=$2
resource=$3
system=$4
multipler=$5



path="/home/greg/Desktop/CDFGenerator/data/slack/${namespace}/${workload}/${resource}/${system}-${multipler}/raw/"
mkdir -p ${path}
echo $path

if [ $system == "dc" ] && [ $resource == "cpu" ]; then 
	scp gcusack@c220g5-111019.wisc.cloudlab.us:/mydata/ec/Distributed-Containers/ec_gcm/logs/*.txt ${path}
else
	scp gcusack@c220g5-111019.wisc.cloudlab.us:~/Autopilot/RL/${namespace}/${resource}_limits/* ${path}
fi

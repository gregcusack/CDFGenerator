#!/bin/bash

namespace=$1
workload=$2
resource=$3
system=$4
period=$5


path="/home/greg/Desktop/CDFGenerator/data/slack/${namespace}/${workload}/${resource}/${system}-${period}s/raw/"
mkdir -p ${path}


scp gcusack@c220g5-111019.wisc.cloudlab.us:~/Autopilot/RL/${namespace}/${resource}_limits/* ${path}

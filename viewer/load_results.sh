#!/bin/bash
export RESULTS=$HOME/mpsforensics/results/results.json
$HOME/mpsforensics/viewer/parse_results.pl > $RESULTS
mongoimport -h localhost:3001 --db meteor --collection str --type json --drop --file $RESULTS --jsonArray
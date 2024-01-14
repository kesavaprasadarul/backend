#!/usr/bin/env bash
for year in {2020..2023}
do
    # invoke endpoint for each month of given years
    for month in {1..12}
    do
        echo "calling http://localhost:8000/api/v1/bundestag_top_topics/?month=$month&year=$year" && \
        curl -X 'POST' "http://localhost:8000/api/v1/bundestag_top_topics/?month=$month&year=$year" -H 'accept: application/json' -d '' && echo " ... finished"
    done

    # invoke for entire year
    echo "calling http://localhost:8000/api/v1/bundestag_top_topics/?year=$year"
    curl -X 'POST' "http://localhost:8000/api/v1/bundestag_top_topics/?year=$year" -H 'accept: application/json' -d ''
done

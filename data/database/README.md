# Instructions

## Load txt file in db
(Prerequisites: Running backend containers by running following command in root $docker compose up )

1. docker compose cp /data/database/<top-topics-file> db:.
2. docker compose db bash (or alternatively attach shell to docker container VSCode via clicking by docker icon on the left menu bar > left-click on postgres container > attach Shell)
3. \COPY top_topics FROM <top-topics-file> DELIMITER ','

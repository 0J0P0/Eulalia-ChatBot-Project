#!/bin/bash

echo "--------------------------------------------------"
echo "Starting!"

python ./EulaliaGPT/MacSqlUtils/run.py \
         --input_file "./EulaliaGPT/MacSqlUtils/input_automated.json" \
         --db_path "" \
         --output_file "./EulaliaGPT/MacSqlUtils/output_eulaliadb_automated.json" \
         --log_file "./EulaliaGPT/MacSqlUtils/log.txt" \
         --tables_json_path "./EulaliaGPT/MacSqlUtils/tables_data.json" \
        #  --without_selector

echo "Generate SQL on test data!"
echo "Done!"
echo "--------------------------------------------------"
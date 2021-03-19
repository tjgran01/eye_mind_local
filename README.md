1. pre-proc/unzip_dir.py
2. pre-proc/create_data_state_table.py
3. pre-proc/stage_files_for_toolbox.py
4. updating_triggers/add_durations_to_triggers.py
5. updating_triggers/push_triggers_to_nirs.py

Should net you ./data/test_long_stim/ parent dir. This can be loaded into toolbox.

6. ./toolbox_code/loading_eml.m
7. ./toolbox_code/eml_pipeline.m

Note: It will take a long time for data to be fit to GLM. (Like, half a day.)

Note: If you get OSERRORS. Make the directories it cannot find (they will be mentioned in the error).

# Check service status
python run_check_study_service_status.py --global_config_yaml resources/tekenradar/config.yaml

# Create study
python run_create_study.py --global_config_yaml resources/tekenradar/config.yaml --study_def_path resources/tekenradar/study

# Update study rules:
python run_update_study_rules.py --global_config_yaml resources/tekenradar/config.yaml --rules_json_path resources/tekenradar/study/study_rules.json --study_key default

# Save survey
python run_save_survey.py --global_config_yaml resources/tekenradar/config.yaml --study_key default --survey_json resources/tekenradar/study/surveys/PDiff.json

# Download responses
python run_response_downloader.py --global_config_yaml resources/tekenradar/config.yaml --study_key default --survey_info_lang nl --survey_info_format json --response_format wide --short_keys --query_start_date 2022-01-01-00-00-00 --query_end_date 2022-02-01-00-00-00 --survey_key PDiff
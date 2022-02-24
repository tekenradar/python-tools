# Check service status
python run_check_study_service_status.py --global_config_yaml resources/tekenradar/config.yaml

# Create study
python run_create_study.py --global_config_yaml resources/tekenradar/config.yaml --study_def_path resources/tekenradar/study

# Update study rules:
python run_update_study_rules.py --global_config_yaml resources/tekenradar/config.yaml --rules_json_path resources/tekenradar/study/study_rules.json --study_key tekenradar

# Save survey
python run_save_survey.py --global_config_yaml resources/tekenradar/config.yaml --study_key tekenradar --survey_json resources/tekenradar/study/surveys/PDiff.json

# Batch save survey
python run_batch_save_surveys.py --global_config_yaml resources/tekenradar/config.yaml --study_key tekenradar --survey_list resources/tekenradar/study/survey_list.txt


# Download participant states and reports
python run_participant_state_downloader.py --global_config_yaml resources/tekenradar/config.yaml --study_key tekenradar
python run_participant_state_downloader.py --global_config_yaml resources/tekenradar/config.yaml --study_key tekenradar --status active
python run_report_history_downloader.py --global_config_yaml resources/tekenradar/config.yaml --study_key tekenradar
python run_report_history_downloader.py --global_config_yaml resources/tekenradar/config.yaml --study_key tekenradar --report_key test1 --query_start_date 2022-01-01-00-00-00 --query_end_date 2022-02-01-00-00-00 --participant_id <id-of-a-participant>

# Download responses
python run_response_downloader.py --global_config_yaml resources/tekenradar/config.yaml --study_key tekenradar --survey_info_lang nl --survey_info_format json --response_format wide --short_keys --query_start_date 2022-01-01-00-00-00 --query_end_date 2022-03-01-00-00-00 --survey_key PDiff
python run_batch_response_downloader.py --global_config_yaml resources/tekenradar/config.yaml --query resources/tekenradar/study/response_query.yaml

## Confidential response downloader
python run_confidential_response_downloader.py --global_config_yaml resources/tekenradar/config.yaml --study_key tekenradar --condition_path resources/tekenradar/study/confidentialResponseDonwloadCondition.json --participants_list resources/tekenradar/study/participants.txt


### Commands for testing
# Change timing of follow ups to now
python3 run_custom_study_rules.py --global_config_yaml resources/tekenradar/config.yaml --rules_json_path ../../tekenradar-studies/output/tekenradar/customRules/changeFollowupTimingToNow.json --study_key tekenradar


### Email Uploading
# Upload common/required email templates:
python run_messaging_upload_common_templates.py --global_config_yaml resources/tekenradar/config.yaml --default_language nl --email_template_folder resources/tekenradar/emails/general-templates

# Upload one custom email template:
python run_messaging_upload_custom_template.py --global_config_yaml resources/tekenradar/config.yaml --email_template_folder resources/tekenradar/emails/custom-templates/testmessage1

# Manage auto email schedules:
python run_messaging_schedule_editor.py --global_config_yaml resources/tekenradar/config.yaml --email_folder resources/tekenradar/emails/message-schedules/participant-message

# Send one message to study participants based using study rule as condition:
# TODO

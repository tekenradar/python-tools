# Check service status
python run_check_study_service_status.py --global_config_yaml resources/tekenradar/config.yaml

# Study managment
##  Create study
python run_create_study.py --global_config_yaml resources/tekenradar/config.yaml --study_def_path resources/tekenradar/study

## Update study rules:
python run_update_study_rules.py --global_config_yaml resources/tekenradar/config.yaml --rules_json_path resources/tekenradar/study/study_rules.json --study_key tekenradar

## Manage study members
python run_manage_study_members.py  --global_config_yaml resources/tekenradar/config.yaml --study_key tekenradar --user_id <userId> --user_name <userName> --action <ADD or REMOVE>

## Manage study's notification subscriptions
python run_manage_study_notification_subs.py --global_config_yaml resources/tekenradar/config.yaml --study_key tekenradar

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
python run_response_downloader.py --global_config_yaml resources/tekenradar/config.yaml --study_key tekenradar --survey_info_lang nl --survey_info_format json --response_format wide --short_keys --query_start_date 2022-01-01-00-00-00 --query_end_date 2022-04-01-00-00-00 --survey_key TBflow_Adults
python run_batch_response_downloader.py --global_config_yaml resources/tekenradar/config.yaml --query resources/tekenradar/study/response_query.yaml

## Confidential response downloader
python run_confidential_response_downloader.py --global_config_yaml resources/tekenradar/config.yaml --study_key tekenradar --condition_path resources/tekenradar/study/confidentialResponseDownloadCondition.json --participants_list resources/tekenradar/study/participants.txt

## Download file infos/files
python run_download_file_infos.py --global_config_yaml resources/tekenradar/config.yaml --study_key tekenradar --query_start_date 2022-01-01-00-00-00 --query_end_date 2022-04-01-00-00-00
python run_download_files.py --global_config_yaml resources/tekenradar/config.yaml --study_key tekenradar --query_start_date 2022-01-01-00-00-00 --query_end_date 2022-04-01-00-00-00


### Commands for testing
# Change timing of follow ups to now
python3 run_custom_study_rules.py --global_config_yaml resources/tekenradar/config.yaml --rules_json_path ../../tekenradar-studies/output/tekenradar/customRules/changeFollowupTimingToNow.json --study_key tekenradar
python3 run_custom_study_rules_for_participants.py --global_config_yaml resources/tekenradar/config.yaml --rules_json_path ../../tekenradar-studies/output/tekenradar/customRules/changeFollowupTimingToNow.json --study_key tekenradar  --participants_ids resources/tekenradar/study/participants.txt

#delete old contact data (zonder 3!!!)
python run_custom_study_rules.py --global_config_yaml resources/tekenradar/config.yaml --rules_json_path ../../tekenradar-studies/output/tekenradar/customRules/assignDeleteContactDataSurvey.json --study_key tekenradar

### Email Uploading
# Upload common/required email templates:
python run_messaging_upload_common_templates.py --global_config_yaml resources/tekenradar/config.yaml --default_language nl --email_template_folder resources/tekenradar/emails/general-templates

# Upload one custom email template:
python run_messaging_upload_custom_template.py --global_config_yaml resources/tekenradar/config.yaml --email_template_folder resources/tekenradar/emails/custom-templates/testmessage1
python run_batch_upload_custom_templates.py --global_config_yaml resources/tekenradar/config.yaml --folder_with_all_templates resources/tekenradar/emails/custom-templates

# Manage auto email schedules:
python run_messaging_schedule_editor.py --global_config_yaml resources/tekenradar/config.yaml --email_folder resources/tekenradar/emails/message-schedules/participant-message
python run_messaging_schedule_editor.py --global_config_yaml resources/tekenradar/config.yaml --email_folder resources/tekenradar/emails/message-schedules/reminder-for-weeklyTB
python run_messaging_schedule_editor.py --global_config_yaml resources/tekenradar/config.yaml --email_folder resources/tekenradar/emails/message-schedules/researcher-notification
python run_messaging_delete_schedule.py --global_config_yaml resources/tekenradar/config.yaml

# Send one message to study participants based using study rule as condition:
# TODO


# Invite users / Migrate users from old system
python prepare_user_migration_files.py --input Invitees2.csv
python run_invite_users.py --global_config_yaml resources/tekenradar/config.yaml  --user_list resources/tekenradar/inviteUsers.json --sleep 2.5


# Longcovid study invite example:
python run_invite_to_external_study_rules.py --global_config_yaml resources/infectieradar/config.yaml --study_key longcovid --participants resources/infectieradar/participants_to_invite.csv
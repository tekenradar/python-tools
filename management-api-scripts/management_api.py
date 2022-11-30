import json
from time import sleep
import requests
from getpass import getpass


class ManagementAPIClient:
    def __init__(self, management_api_url, login_credentials=None, participant_api_url=None, use_external_idp=False, use_no_login=False):
        self.management_api_url = management_api_url
        self.participant_api_url = participant_api_url

        if use_no_login:
            return

        self.token = None
        self._refresh_token = None
        self.auth_header = None
        print('Initilize client')
        if login_credentials is None:
            print('No auth infos found. Exiting.')
            exit()

        if use_external_idp:
            self.login_with_saml(login_credentials)
        else:
            self.login(login_credentials)

    def check_study_service_status(self):
        r = requests.get(self.participant_api_url + '/v1/status/study-service')
        if r.status_code != 200:
            raise ValueError(r.content)
        print(r.content)

    def login_with_saml(self, auth_infos):
        print("##################################")
        link = "{}/v1/auth/login-with-saml?instance={}&role={}".format(
            self.management_api_url, auth_infos["instanceId"], auth_infos["role"])
        print("Start login flow. Please open the following link in a browser:")
        print("\n\n{}\n\n".format(link))
        sleep(5)

        print("Please enter the token string displayed in the browser window after login:")
        tokens = getpass("Token: ")
        tparts = tokens.split("<!>")
        counter = 0
        while len(tparts) != 2:
            print("Unexpected token string. Please make sure, you copy the right text.")
            counter += 1
            if counter > 5:
                print("Something went wrong. Exiting.")
                exit()
            tokens = getpass("Token: ")
            tparts = tokens.split("_")

        self.token = tparts[0]
        self._refresh_token = tparts[1]
        self.auth_header = {'Authorization': 'Bearer ' + self.token}
        print("\n\nFinished login flow.")
        print("##################################")

    def login(self, credentials):
        r = requests.post(
            self.management_api_url + '/v1/auth/login-with-email', data=json.dumps(credentials))
        if r.status_code != 200:
            print(r.content)
            exit()
        resp = r.json()
        if 'secondFactorNeeded' in resp.keys() and resp['secondFactorNeeded']:
            verification_code = input('Enter verification code:')
            credentials['verificationCode'] = verification_code.replace('-', '').replace(' ', '').strip()
            r = requests.post(
                self.management_api_url + '/v1/auth/login-with-email', data=json.dumps(credentials))
            if r.status_code != 200:
                print(r.content)
                exit()
            resp = r.json()

        self.token = resp['token']['accessToken']
        self._refresh_token = resp['token']['refreshToken']
        self.auth_header = {'Authorization': 'Bearer ' + self.token}
        print('Successfully logged in.')

    def renew_token(self):
        """
        export const renewTokenURL = '/v1/auth/renew-token';
        export const renewTokenReq = (refreshToken: string) => authApiInstance.post<TokenResponse>(renewTokenURL, { refreshToken: refreshToken });
        :return:
        """
        if self.auth_header is None:
            raise ValueError('need to login first')
        if self.participant_api_url is None:
            raise ValueError('missing common api url')
        r = requests.post(self.participant_api_url + '/v1/auth/renew-token',
                          headers=self.auth_header, data=json.dumps({"refreshToken": self._refresh_token}))
        if r.status_code != 200:
            raise ValueError(r.content)
        resp = r.json()
        self.token = resp['accessToken']
        self._refresh_token = resp['refreshToken']
        self.auth_header = {'Authorization': 'Bearer ' + self.token}

    def create_study(self, study_obj):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.post(self.management_api_url + '/v1/studies',
                          headers=self.auth_header, data=json.dumps(study_obj))
        if r.status_code != 200:
            raise ValueError(r.content)
        print('study created succcessfully')

    def update_study_props(self, study_key, props):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.post(self.management_api_url + '/v1/study/' + study_key + '/props', headers=self.auth_header,
                          data=json.dumps({
                              'studyKey': study_key,
                              'props': props
                          }))
        if r.status_code != 200:
            raise ValueError(r.content)
        print('study props updated succcessfully')

    def get_study_notification_subs(self, study_key):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.get(self.management_api_url + '/v1/study/' + study_key + '/notification-subscriptions', headers=self.auth_header)
        if r.status_code != 200:
            raise ValueError(r.content)
        return r.json()

    def update_study_notification_subs(self, study_key, subscritions):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.post(self.management_api_url + '/v1/study/' + study_key + '/notification-subscriptions', headers=self.auth_header,
                          data=json.dumps({
                              'subscriptions': subscritions
                          }))
        if r.status_code != 200:
            raise ValueError(r.content)
        print('study notification subscriptions updated succcessfully')
        return r.json()


    def update_study_rules(self, study_key, rules):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.post(self.management_api_url + '/v1/study/' + study_key + '/rules', headers=self.auth_header,
                          data=json.dumps({
                              'studyKey': study_key,
                              'rules': rules
                          }))
        if r.status_code != 200:
            raise ValueError(r.content)
        print('study rules updated succcessfully')

    def run_custom_study_rules(self, study_key, rules):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.post(self.management_api_url + '/v1/study/' + study_key + '/run-rules', headers=self.auth_header,
                          data=json.dumps({
                              'studyKey': study_key,
                              'rules': rules
                          }))
        if r.status_code != 200:
            raise ValueError(r.content)
        return r.json()

    def run_custom_study_rules_for_single_participant(self, study_key, rules, participantID: str):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.post(self.management_api_url + '/v1/study/' + study_key + '/run-rules-for-single-participant', headers=self.auth_header,
                          data=json.dumps({
                              'studyKey': study_key,
                              'rules': rules,
                              'participantId': participantID,
                          }))
        if r.status_code != 200:
            raise ValueError(r.content)
        return r.json()
        # print('study rules updated succcessfully')

    def delete_study(self, study_key):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.delete(self.management_api_url + '/v1/study/' +
                            study_key, headers=self.auth_header)
        if r.status_code != 200:
            raise ValueError(r.content)
        print('study deleted succcessfully')

    def add_study_member(self, study_key, user_id, user_name, role='maintainer'):
        if self.auth_header is None:
            raise ValueError('need to login first')
        self.post = requests.post(self.management_api_url + '/v1/study/' + study_key + '/save-member',
                                  headers=self.auth_header,
                                  data=json.dumps({
                                      'studyKey': study_key,
                                      'member': {
                                          "userId": user_id,
                                          "role": role,
                                          "username": user_name
                                      }
                                  }))
        r = self.post
        if r.status_code != 200:
            raise ValueError(r.content)
        print('user successfully added to study')

    def remove_study_member(self, study_key, user_id):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.post(self.management_api_url + '/v1/study/' + study_key + '/remove-member',
                          headers=self.auth_header,
                          data=json.dumps({
                              'studyKey': study_key,
                              'member': {
                                  "userId": user_id,
                              }
                          })
                          )
        if r.status_code != 200:
            raise ValueError(r.content)
        print('user successfully removed from study')

    def save_survey_to_study(self, study_key, survey_object):
        if self.auth_header is None:
            raise ValueError('need to login first')

        upload_obj = {
            "studyKey": study_key,
            "survey": survey_object
        }
        r = requests.post(self.management_api_url + '/v1/study/' + study_key +
                          '/surveys', headers=self.auth_header, data=json.dumps(upload_obj))
        if r.status_code != 200:
            raise ValueError(r.content)
        print('survey saved succcessfully')

    def get_surveys_in_study(self, study_key):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.get(self.management_api_url + '/v1/study/' +
                         study_key + '/surveys', headers=self.auth_header)
        if r.status_code != 200:
            raise ValueError(r.content)
        return r.json()

    def get_survey_definition(self, study_key, survey_key, version_id=''):
        if self.auth_header is None:
            raise ValueError('need to login first')
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.get(
            self.management_api_url + '/v1/study/' + study_key + '/survey/' + survey_key + '/' + version_id,
            headers={'Authorization': 'Bearer ' + self.token})
        if r.status_code != 200:
            if json.loads(r.content.decode())["error"] == "mongo: no documents in result":
                print('Survey key does not exist in this study yet.')
            else:
                print(r.content)
            return None
        return r.json()

    def get_survey_keys(self, study_key):
        if self.auth_header is None:
            raise ValueError('need to login first')
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.get(
            self.management_api_url + '/v1/study/' + study_key + '/survey-keys',
            headers={'Authorization': 'Bearer ' + self.token})
        if r.status_code != 200:
            if json.loads(r.content.decode())["error"] == "mongo: no documents in result":
                print('Survey keys does not exist in this study yet.')
            else:
                print(r.content)
            return None
        return r.json()

    def get_survey_history(self, study_key, survey_key):
        if self.auth_header is None:
            raise ValueError('need to login first')
        if self.auth_header is None:
            raise ValueError('need to login first')
        url = '{}/v1/study/{}/survey/{}/versions'.format(self.management_api_url, study_key, survey_key)
        r = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})
        if r.status_code != 200:
            if json.loads(r.content.decode())["error"] == "mongo: no documents in result":
                print('Survey does not exist in this study yet.')
            else:
                print(r.content)
            return None
        return r.json()

    def unpublish_survey(self, study_key, survey_key):
        if self.auth_header is None:
            raise ValueError('need to login first')
        url = '{}/v1/study/{}/survey/{}'.format(self.management_api_url, study_key, survey_key)
        r = requests.delete(
            url,
            headers={'Authorization': 'Bearer ' + self.token})
        if r.status_code != 200:
            raise ValueError(r.content)
        print("survey successfully unpublished")

    def remove_survey_version(self, study_key, survey_key, version_id):
        if self.auth_header is None:
            raise ValueError('need to login first')
        url = '{}/v1/study/{}/survey/{}/{}'.format(self.management_api_url, study_key, survey_key, version_id)
        r = requests.delete(
            url,
            headers={'Authorization': 'Bearer ' + self.token})
        if r.status_code != 200:
            raise ValueError(r.content)
        print("survey successfully removed")

    def get_participant_states(self, study_key: str, status:str=None):
        if self.auth_header is None:
            raise ValueError('need to login first')
        url = "{}/v1/data/{}/participants".format(
                self.management_api_url,
                study_key,
            )

        if status is not None:
            params = {
                "status": status
            }
        else:
            params = None
        r = requests.get(url, headers=self.auth_header, params=params)
        if r.status_code != 200:
            print(r.content)
            return None
        return r.json()

    def get_participant_reports(self, study_key: str, report_key:str=None, participant_id:str=None, since:float=None, until:float=None):
        if self.auth_header is None:
            raise ValueError('need to login first')
        url = "{}/v1/data/{}/reports".format(
                self.management_api_url,
                study_key,
            )

        params = {}
        if report_key is not None:
            params["reportKey"] = report_key
        if participant_id is not None:
            params["participant"] = participant_id
        if since is not None:
            params["from"] = since
        if until is not None:
            params["until"] = until
        r = requests.get(url, headers=self.auth_header, params=params)
        if r.status_code != 200:
            print(r.content)
            return None
        return r.json()

    def get_file_infos(self, study_key: str, file_type:str=None, participant_id:str=None, since:float=None, until:float=None):
        if self.auth_header is None:
            raise ValueError('need to login first')
        url = "{}/v1/data/{}/file-infos".format(
                self.management_api_url,
                study_key,
            )

        params = {}
        if file_type is not None:
            params["fileType"] = file_type
        if participant_id is not None:
            params["participant"] = participant_id
        if since is not None:
            params["from"] = since
        if until is not None:
            params["until"] = until
        r = requests.get(url, headers=self.auth_header, params=params)
        if r.status_code != 200:
            print(r.content)
            return None
        return r.json()

    def download_file(self, study_key: str, file_id:str):
        if self.auth_header is None:
            raise ValueError('need to login first')
        url = "{}/v1/data/{}/file".format(
                self.management_api_url,
                study_key,
            )

        params = {}
        params["id"] = file_id
        r = requests.get(url, headers=self.auth_header, params=params)
        if r.status_code != 200:
            print(r.content)
            return None
        return r.content

    def get_confidential_responses(self, study_key: str, query):
        if self.auth_header is None:
            raise ValueError('need to login first')
        url = "{}/v1/data/{}/fetch-confidential-responses".format(
                self.management_api_url,
                study_key,
            )
        r = requests.post(url, headers=self.auth_header, data=json.dumps(query))
        if r.status_code != 200:
            print(r.content)
            return None
        return r.json()

    def get_response_statistics(self, study_key, start=None, end=None):
        if self.auth_header is None:
            raise ValueError('need to login first')
        params = {}
        if start is not None:
            params["from"] = int(start)
        if end is not None:
            params["until"] = int(end)
        r = requests.get(
            self.management_api_url + '/v1/data/' + study_key + '/statistics',
            headers={'Authorization': 'Bearer ' + self.token}, params=params)
        if r.status_code != 200:
            raise ValueError(r.content)
        return r.json()

    def get_survey_responses(self, study_key, survey_key=None, start=None, end=None):
        if self.auth_header is None:
            raise ValueError('need to login first')
        if self.token is None:
            raise ValueError('need to login first')
        params = {}
        if survey_key is not None:
            params["surveyKey"] = survey_key
        if start is not None:
            params["from"] = int(start)
        if end is not None:
            params["until"] = int(end)
        r = requests.get(
            self.management_api_url + '/v1/data/' + study_key + '/responses', headers=self.auth_header, params=params)
        if r.status_code != 200:
            print(r.content)
            return None
        return r.json()

    def get_response_csv(self,
                         study_key: str,
                         survey_key: str,
                         key_separator: str,
                         format=str,
                         short_keys=True,
                         with_meta_infos=None,
                         start=None,
                         end=None
                         ):
        if self.auth_header is None:
            raise ValueError('need to login first')
        if self.token is None:
            raise ValueError('need to login first')
        params = {}
        params["sep"] = key_separator
        if with_meta_infos is not None:
            params = {**params, **with_meta_infos}
        if start is not None:
            params["from"] = int(start)
        if end is not None:
            params["until"] = int(end)

        if short_keys:
            params["shortKeys"] = "true"
        else:
            params["shortKeys"] = "false"

        url = "{}/v1/data/{}/survey/{}/response".format(
            self.management_api_url,
            study_key,
            survey_key,
        )
        if format == "long":
            url = "{}/v1/data/{}/survey/{}/response/long-format".format(
                self.management_api_url,
                study_key,
                survey_key,
            )
        elif format == "json":
            url = "{}/v1/data/{}/survey/{}/response/json".format(
                self.management_api_url,
                study_key,
                survey_key,
            )

        r = requests.get(url, headers=self.auth_header, params=params)
        if r.status_code != 200:
            print(r.content)
            return None
        return r.text

    def get_survey_info_preview_csv(self,
                                    study_key: str,
                                    survey_key: str,
                                    lang: str,
                                    short_keys=True,
                                    ):
        if self.auth_header is None:
            raise ValueError('need to login first')
        if self.token is None:
            raise ValueError('need to login first')
        params = {}
        params["lang"] = lang
        if short_keys:
            params["shortKeys"] = "true"
        else:
            params["shortKeys"] = "false"

        url = "{}/v1/data/{}/survey/{}/survey-info/csv".format(
            self.management_api_url,
            study_key,
            survey_key,
        )

        r = requests.get(url, headers=self.auth_header, params=params)
        if r.status_code != 200:
            print(r.content)
            return None
        return r.text

    def get_survey_info_preview(self,
                                study_key: str,
                                survey_key: str,
                                lang: str,
                                short_keys=True,
                                ):
        if self.auth_header is None:
            raise ValueError('need to login first')
        if self.token is None:
            raise ValueError('need to login first')
        params = {}
        params["lang"] = lang
        if short_keys:
            params["shortKeys"] = "true"
        else:
            params["shortKeys"] = "false"

        url = "{}/v1/data/{}/survey/{}/survey-info".format(
            self.management_api_url,
            study_key,
            survey_key,
        )

        r = requests.get(url, headers=self.auth_header, params=params)
        if r.status_code != 200:
            print(r.content)
            return None
        return r.json()

    def get_all_templates(self):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.get(
            self.management_api_url + '/v1/messaging/email-templates', headers=self.auth_header)
        if r.status_code != 200:
            raise ValueError(r.content)
        return r.json()

    def save_email_template(self, template_object):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.post(self.management_api_url + '/v1/messaging/email-templates',
                          data=json.dumps({'template': template_object}), headers=self.auth_header)
        if r.status_code != 200:
            raise ValueError(r.content)
        return r.json()

    def delete_email_template(self, message_type, study_key=None):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.post(self.management_api_url + '/v1/messaging/email-templates/delete',
                          data=json.dumps({
                              'messageType': message_type,
                              'studyKey': study_key,
                          }), headers=self.auth_header)
        if r.status_code != 200:
            raise ValueError(r.content)
        print('email template deleted successfully')

    def delete_auto_message(self, auto_message_id):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.delete(self.management_api_url + '/v1/messaging/auto-message/' +
                            auto_message_id, headers=self.auth_header)
        if r.status_code != 200:
            raise ValueError(r.content)
        print('auto message deleted successfully')

    def get_auto_messages(self):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.get(
            self.management_api_url + '/v1/messaging/auto-messages', headers=self.auth_header)
        if r.status_code != 200:
            raise ValueError(r.content)
        return r.json()

    def save_auto_message(self, auto_message_object):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.post(
            self.management_api_url + '/v1/messaging/auto-messages', data=json.dumps(auto_message_object),
            headers=self.auth_header)
        if r.status_code != 200:
            raise ValueError(r.content)
        print('auto message saved successfully')

    def send_message_to_all_users(self, template_object, ignore_weekday=False):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.post(
            self.management_api_url + '/v1/messaging/send-message/all-users',
            data=json.dumps({
                "template": template_object,
                "ignoreWeekday": ignore_weekday,
                }), headers=self.auth_header)
        if r.status_code != 200:
            raise ValueError(r.content)
        print('message sending triggered')

    def send_message_to_study_participants(self, study_key, condition, template_object, ignore_weekday=False):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.post(
            self.management_api_url + '/v1/messaging/send-message/study-participants', data=json.dumps({
                "studyKey": study_key,
                "condition": condition,
                "template": template_object,
                "ignoreWeekday": ignore_weekday,
            }), headers=self.auth_header)
        if r.status_code != 200:
            raise ValueError(r.content)
        print('message sending triggered')

    def migrate_user(self, user_object):
        if self.auth_header is None:
            raise ValueError('need to login first')
        r = requests.post(
            self.management_api_url + '/v1/user/migrate', data=json.dumps(user_object), headers=self.auth_header)
        if r.status_code != 200:
            raise ValueError(r.json())
        print('user created for ' + user_object['accountId'])

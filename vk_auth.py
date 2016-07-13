#coding utf8
import requests
from html.parser import HTMLParser

class FormParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.url         = None
        self.denial_url  = None
        self.params      = {}
        self.method      = 'GET'
        self.in_form     = False
        self.in_denial   = False
        self.form_parsed = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == 'form':
            if self.in_form:
                raise RuntimeError('Nested form tags are not supported yet')
            else:
                self.in_form = True
        if not self.in_form:
            return

        attrs = dict((name.lower(), value) for name, value in attrs)

        if tag == 'form':
            self.url = attrs['action']
            if 'method' in attrs:
                self.method = attrs['method']
        elif tag == 'input' and 'type' in attrs and 'name' in attrs:
            if attrs['type'] in ['hidden', 'text', 'password']:
                self.params[attrs['name']] = attrs['value'] if 'value' in attrs else ''
        elif tag == 'input' and 'type' in attrs:
            if attrs['type'] == 'submit':
                self.params['submit_allow_access'] = True
        elif tag == 'div' and 'class' in attrs:
            if attrs['class'] = 'near_btn':
                self.in_denial = True
        elif tag == 'a' and 'href' in attrs and self.in_denial:
            self.denial_url = attr['href']

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == 'form':
            if not self.in_form:
                raise RuntimeError('Unexpected end of <form>')
            self.form_parsed = True
            self.in_form = False
        elif tag == 'div' and self.in_denial:
            self.in_denial = False


class VKAuth(object):

    def __init__(self, permissions, app_id, api_v, email=None, pswd=None, two_factor_auth=False, security_code=None, auto_access=True):
        """
        Args:
            permissions: list of Strings with permissions to get from API
            app_id: (String) vk app id that one can get from vk.com
            api_v: (String) vk API version
        """

        self.session        = requests.Session()
        self.form_parser    = FormParser()
        self.user_id        = None
        self.access_token   = None
        self.response       = None

        self.permissions    = permissions
        self.api_v          = api_v
        self.app_id         = app_id
        self.two_factor_auth= two_factor_auth
        self.security_code  = security_code
        self.email          = email
        self.pswd           = pswd
        self.auto_access    = auto_access

        if security_code != None and two_factor_auth == False:
            raise RuntimeError('Security code provided for non-two-factor authorization')

    def print_cookies(self):
        print(self.session.cookies)


    def authorize(self):

        api_auth_url = 'https://oauth.vk.com/authorize'
        app_id = self.app_id
        permissions = self.permissions
        redirect_uri = 'https://oauth.vk.com/blank.html'
        display = 'wap'
        api_version = self.api_v

        auth_url_template = '{0}?client_id={1}&scope={2}&redirect_uri={3}&display={4}&v={5}&response_type=token'
        auth_url = auth_url_template.format(api_auth_url, app_id, ','.join(permissions), redirect_uri, display, api_version)

        self.print_cookies()
        self.response = self.session.get(auth_url)
        self.print_cookies()

        #look for <form> element in response html and parse it
        if not self._parse_form():
            raise RuntimeError('No <form> element found. Please, check url address')
        else:
            # try to log in with email and password (stored or expected to be entered)
            while not self._log_in():
                pass;
            self.print_cookies()

            # handling two-factor authentication
            # expecting a security code to enter here
            if self.two_factor_auth:
                self._two_fact_auth()

            # allow vk to use this app and access self.permissions
            self._allow_access()

            # now get access_token and user_id
            self._get_params()

    def _parse_form(self):

        self.form_parser = FormParser()
        parser = self.form_parser
        try:
            parser.feed(str(self.response.content))
        except:
            print('Unexpected error occured while looking for <form> element')
            return False

        return True

    def _submit_form(self, *params):

        parser = self.form_parser
        if parser.method == 'post':
            payload = parser.params
            payload.update(*params)
            try:
                self.response = self.session.post(parser.url, data=payload)
            except:
                print('Runtime Error: couldn\'t make POST request. Check your email and password')

        else:
            self.response = None

    def _log_in(self):

        if self.email == None:
            self.email = ''
            while self.email.strip() == '':
                self.email = input('Enter an email to log in: ')

        if self.pswd == None:
            self.pswd = ''
            while self.pswd.strip() == '':
                self.pswd = input('Enter the password: ')

        self._submit_form({'email': self.email, 'pass': self.pswd})
        if not self._parse_form():
            raise RuntimeError('No <form> element found. Please, check url address')

        # if wrong email or password
        if 'pass' in self.form_parser.params:
            print('Wrong email or password')
            self.email = None
            self.pswd = None
            return False
        elif 'code' in self.form_parser.params and not self.two_factor_auth:
            raise RuntimeError('Two-factor authentication expected from VK.\nChange `two_factor_auth` to `True` and provide a security code.')
        else:
            return True

    def _two_fact_auth(self):

        prefix = 'https://m.vk.com'
        if prefix not in self.form_parser.url:
            self.form_parser.url = prefix + self.form_parser.url

        if self.security_code == None:
            self.security_code = input('Enter security code for two-factor authentication: ')

        self._submit_form({'code': self.security_code})

        if not self._parse_form():
            raise RuntimeError('No <form> element found. Please, check url address')

    def _allow_access(self):
        parser = self.form_parser

        if 'submit_allow_access' in parser.params and 'grant_access' in parser.url:
            if not self.auto_access:
                answer = ''
                msg =   'Application needs access to the following details in your profile:\n' + \
                        str(self.permissions) + '\n' + \
                        'Allow it to use them? (yes or no)'

                attempts = 5
                while answer not in ['yes', 'no'] and attempts > 0:
                    answer = input(msg).lower().strip()
                    attempts-=1

                if answer == 'no' or attempts == 0:
                    self.form_parser.url = self.form_parser.denial_url
                    print('Access denied')

            self._submit_form({})

    def _get_params(self):

        try:
            params = self.response.url.split('#')[1].split('&')
            self.access_token = params[0].split('=')[1]
            self.user_id = params[2].split('=')[1]
        except IndexError(e):
            print(e)
            print('Coudln\'t fetch token')

    def kill(self):
        self.session.close()
        self.session        = None
        self.form_parser    = None
        self.user_id        = None
        self.access_token   = None
        self.response       = None

        self.permissions    = None
        self.api_v          = None
        self.app_id         = None
        self.two_factor_auth= None
        self.security_code  = None
        self.email          = None
        self.pswd           = None

    def close(self):
        self.session.close()
        self.response = None
        self.form_parser = None
        self.security_code = None
        self.email = None
        self.pswd = None


"""
    implement reset() for form_parser
    exception handling
    make readme more descriptive
    tune up _get_params method
"""
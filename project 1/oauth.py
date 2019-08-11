import json
import string
import requests
from rauth import OAuth2Service
from flask import current_app, url_for, request, redirect, session
import random




def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

def refresh_token():
    if not expired():
        return

    # OAuth 2.0 example
    data = {'client_id':client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token}

    return service.get_access_token(data=data)

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']
        self.state = ''.join(random.choice(string.ascii_uppercase) for i in range(10))

    def authorize(self):
        pass

    def callback(self):
        pass

    
    def validate_oauth2callback(self):
        if 'code' not in request.args: #dump request if problem
            abort(500, 'oauth2 callback: code not in request.args: \n' + str(request.__dict__))
        if request.args.get('state') != session.get('state'):
            abort(500, 'oauth2 callback: state does not match: \n' + str(request.__dict__))


    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]




class GitHubSignIn(OAuthSignIn):  
    def __init__(self):
        super(GitHubSignIn, self).__init__('github')
        self.service = OAuth2Service(
            name='github',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://github.com/login/oauth/authorize',
            access_token_url='https://github.com/login/oauth/access_token',
            base_url='https://api.github.com/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
                state=self.state,
                redirect_uri=self.get_callback_url())
            )

    def callback(self):
        self.validate_oauth2callback()
        #get token
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('user').json()
        social_id = 'github$' + str(me['id'])
        nickname = me['login']
        email = None
        url = 'https://github.com/' + me['login'] #TODO: be sure this isn't changed
        return (social_id, nickname, email, url, me)
        

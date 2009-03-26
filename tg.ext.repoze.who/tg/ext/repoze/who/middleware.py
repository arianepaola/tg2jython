# sample plugins and middleware configuration for tg2 

class SQLAuthenticatorPlugin:
    def __init__(self, user_class, session_factory, user_criterion,
            user_id_col):
        self.user_class = user_class
        self.user_criterion = user_criterion
        self.session_factory = session_factory
        self.user_id_col = user_id_col

    # IAuthenticator
    def authenticate(self, environ, identity):
        if not 'login' in identity:
            return None

        session = self.session_factory()

        query = session.query(self.user_class)
        query = query.filter(
                self.user_criterion==identity['login'])
        user = query.first()

        if user:
            if user.validate_password(identity['password']):
                # grab the attr value that serves as a unique identifier
                # for the user column; this may be either an integer,
                # a string, or a unicode value
                return getattr(user, self.user_id_col)

class SQLMetadataProviderPlugin:
    def __init__(self, user_class, session_factory, criterion_token):
        self.session_factory = session_factory
        self.user_class = user_class
        self.criterion_token = criterion_token

    # IMetadataProvider
    def add_metadata(self, environ, identity):
        session = self.session_factory()
        query = session.query(self.user_class)

        id_ = identity['repoze.who.userid']
        user = query.get(id_)
        
        # at this point, identity['user'] is either None or a
        # yourapp.model.User class
        identity['user'] = user

        if user:
            # identity['groups'] will be a list of group names
            identity['groups'] = [group.group_name for group in user.groups]

            # identity['permissions'] will be a list of permission names
            identity['permissions'] = [permission.permission_name for
                                       permission in user.permissions]
        else:
            # TODO: I'd like a to be able to give permissions to
            # anonymous users explicitly this means passing a default
            # user object to the sql authenticator so it can be
            # injected when the user is not found...
            identity['groups'] = list()
            identity['permissions'] = list()

def make_who_middleware(app, config, user_class, user_criterion, user_id_col,
        session_factory, form_plugin=None):
    """A sample configuration of repoze.who authentication for TurboGears 2
    """
    sqlauth = SQLAuthenticatorPlugin(user_class, session_factory,
                                     user_criterion, user_id_col)

    allmd = SQLMetadataProviderPlugin(user_class, session_factory,
            user_criterion)

    # use "stock" repoze.who plugins for identification
    from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
    cookie = AuthTktCookiePlugin('secret', 'authtkt')
    
    if form_plugin is None:
        from repoze.who.plugins.form import RedirectingFormPlugin
        form = RedirectingFormPlugin('/login', '/login_handler', '/logout_handler',
                                     rememberer_name='cookie')

    identifiers = [('form', form), ('cookie', cookie)]
    authenticators = [('sqlauth', sqlauth)]
    challengers = [('form', form)]
    mdproviders = [('all', allmd)]

    from repoze.who.classifiers import default_challenge_decider
    from repoze.who.classifiers import default_request_classifier

    log_stream = None
    import os
    if os.environ.get('WHO_LOG'):
        import sys
        log_stream = sys.stdout

    from repoze.who.middleware import PluggableAuthenticationMiddleware
    import logging
    middleware = PluggableAuthenticationMiddleware(
        app,
        identifiers,
        authenticators,
        challengers,
        mdproviders,
        default_request_classifier,
        default_challenge_decider,
        log_stream= log_stream,
        log_level = logging.DEBUG
        )
    return middleware

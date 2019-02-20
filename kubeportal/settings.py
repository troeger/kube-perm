import os
from configurations import Configuration, values


class Common(Configuration):
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'oauth2_provider',
        'corsheaders',
        'social_django',
        'kubeportal',
    ]

    MIDDLEWARE = [
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = 'kubeportal.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'social_django.context_processors.backends',
                    'social_django.context_processors.login_redirect',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'kubeportal.wsgi.application'

    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    AUTHENTICATION_BACKENDS = (
        'social_core.backends.username.UsernameAuth',
        'django.contrib.auth.backends.ModelBackend',
    )

    SOCIAL_AUTH_PIPELINE = (
        'kubeportal.active_directory.user_password',
        'social_core.pipeline.social_auth.social_details',
        'social_core.pipeline.social_auth.social_uid',
        'social_core.pipeline.social_auth.auth_allowed',
        'social_core.pipeline.social_auth.social_user',
        'social_core.pipeline.user.get_username',
        'social_core.pipeline.user.create_user',
        'social_core.pipeline.social_auth.associate_user',
        'social_core.pipeline.social_auth.associate_user',
        'social_core.pipeline.social_auth.load_extra_data',
        'social_core.pipeline.user.user_details',
    )

    SOCIAL_AUTH_USERNAME_FORM_URL = '/login-form/'
    SOCIAL_AUTH_USERNAME_FORM_HTML = 'login_form.html'
    LOGIN_URL = '/social/login/username'

    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    LOGIN_URL = 'index'
    LOGIN_ERROR_URL = 'index'
    LOGOUT_REDIRECT_URL = 'index'
    LOGIN_REDIRECT_URL = 'dashboard'
    STATIC_URL = '/static/'

    CORS_ORIGIN_ALLOW_ALL = True


class Development(Common):
    DEBUG = True
    SECRET_KEY = '4711'
    ALLOWED_HOSTS = []
    LANGUAGE_CODE = 'en-us'
    TIME_ZONE = 'UTC'
    BRANDING = "KubePortal"
    ACTIVE_DIRECTORY_DOMAIN = values.Value(None, environ_prefix='KUBEPORTAL')

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "static"),
    ]

    INSTALLED_APPS = Common.INSTALLED_APPS + ['test_pep8', ]
    TEST_PEP8_IGNORE = ['E501', ]
    PROJECT_DIR = os.path.dirname(__file__)
    TEST_PEP8_DIRS = [os.path.dirname(PROJECT_DIR), ]
    TEST_PEP8_EXCLUDE = ['.env', '.venv', 'env', 'venv', ]


class Production(Common):
    DEBUG = values.Value(False, environ_prefix='KUBEPORTAL')
    SECRET_KEY = values.Value(environ_required=True, environ_prefix='KUBEPORTAL')
    ALLOWED_HOSTS = values.Value(environ_required=True, environ_prefix='KUBEPORTAL')
    LANGUAGE_CODE = values.Value('en-us', environ_prefix='KUBEPORTAL')
    TIME_ZONE = values.Value('UTC', environ_prefix='KUBEPORTAL')
    BRANDING = values.Value('KubePortal', environ_prefix='KUBEPORTAL')
    ACTIVE_DIRECTORY_DOMAIN = values.Value(environ_required=True, environ_prefix='KUBEPORTAL')

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

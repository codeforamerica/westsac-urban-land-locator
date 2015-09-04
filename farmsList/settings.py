# -*- coding: utf-8 -*-
import os

os_env = os.environ

class Config(object):
    SECRET_KEY = os_env.get('FARMSLIST_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    MAIL_SERVER = os_env.get('POSTMARK_SMTP_SERVER')
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os_env.get('POSTMARK_API_TOKEN')
    MAIL_PASSWORD = os_env.get('POSTMARK_API_TOKEN')
    MAIL_DEFAULT_SENDER = "Acres Webmaster <acres.webmaster@acres.online>"

class ProdConfig(Config):
    """Production configuration."""
    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os_env.get('HEROKU_POSTGRESQL_IVORY_URL')
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    HTTP_SERVER = "acres.herokuapp.com"

class DevConfig(Config):
    """Development configuration."""
    ENV = 'dev'
    DEBUG = True
    MAIL_DEBUG = True
    DB_NAME = 'dev.db'
    # Put the db file in project root
    # DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'postgresql://urbanlandlocatoradmin:@localhost/urban_land_locator' #'sqlite:///{0}'.format(DB_PATH)
    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    HTTP_SERVER = "localhost:5001"

class TestConfig(Config):
    """Testing configuration"""
    ENV = 'test'
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 1  # For faster tests
    WTF_CSRF_ENABLED = False  # Allows form testing

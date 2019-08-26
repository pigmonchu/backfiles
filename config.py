class Config(object):
    '''
    Common configurations
    '''

class DevelopmentConfig(object):
    '''
    Dev configurations
    '''

    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(object):
    '''
    Production configurations
    '''

    DEBUG = False
    SQLALCHEMY_ECHO = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig, 
}

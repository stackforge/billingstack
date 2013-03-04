# Server Specific Configurations
server = {
    'port': '9001',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'billingstack.api.root.RootController',
    'modules': ['billingstack.api'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/templates',
    'debug': False,
    'enable_acl': True,
}

logging = {
    'loggers': {
        'root': {'level': 'INFO', 'handlers': ['console']},
        'billingstack': {'level': 'DEBUG', 'handlers': ['console']},
        'wsme': {'level': 'DEBUG', 'handlers': ['console']}
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'formatters': {
        'simple': {
            'format': ('%(asctime)s %(levelname)-5.5s [%(name)s]'
                       '[%(threadName)s] %(message)s')
        }
    },
}

# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
#
# All configurations are accessible at::
# pecan.conf

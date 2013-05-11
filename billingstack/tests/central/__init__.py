from oslo.config import cfg


cfg.CONF.import_opt('storage_driver', 'billingstack.central',
                    group='service:central')
cfg.CONF.import_opt('database_connection',
                    'billingstack.central.storage.impl_sqlalchemy',
                    group='central:sqlalchemy')

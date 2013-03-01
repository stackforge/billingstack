import os
from oslo.config import cfg


cfg.CONF.register_opts([
    cfg.StrOpt('pybasedir',
               default=os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                    '../')),
               help='Directory where the nova python module is installed'),
    cfg.StrOpt('state-path', default='$pybasedir',
               help='Top-level directory for maintaining billingstack\'s state')
])

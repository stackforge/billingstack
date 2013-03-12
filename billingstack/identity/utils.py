import passlib.hash
from oslo.config import cfg
import random
import string

from billingstack import exceptions


cfg.CONF.register_opts([
    cfg.IntOpt('crypt_strength', default=40000)],
    group='service:identity_api')


MAX_PASSWORD_LENGTH = 4096


def generate_random_string(chars=7):
    return u''.join(random.sample(string.ascii_letters * 2 + string.digits,
                    chars))


def trunc_password(password):
    """Truncate passwords to the MAX_PASSWORD_LENGTH."""
    try:
        if len(password) > MAX_PASSWORD_LENGTH:
            return password[:MAX_PASSWORD_LENGTH]
        else:
            return password
    except TypeError:
        raise exceptions.ValidationError(attribute='string', target='password')


def hash_password(password):
    """Hash a password. Hard."""
    password_utf8 = trunc_password(password).encode('utf-8')
    if passlib.hash.sha512_crypt.identify(password_utf8):
        return password_utf8
    h = passlib.hash.sha512_crypt.encrypt(password_utf8,
                                          rounds=cfg.CONF.crypt_strength)
    return h


def check_password(password, hashed):
    """Check that a plaintext password matches hashed.

    hashpw returns the salt value concatenated with the actual hash value.
    It extracts the actual salt if this value is then passed as the salt.

    """
    if password is None:
        return False
    password_utf8 = trunc_password(password).encode('utf-8')
    return passlib.hash.sha512_crypt.verify(password_utf8, hashed)

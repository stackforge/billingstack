import glob
import os.path

import anyjson as json


DIR = os.path.join(os.path.dirname(__file__), 'samples_data')


def get_sample(name):
    """
    Get a sample file .json, for example user.json

    :param name: The name of the sample type
    """
    f = open('%s/%s.json' % (DIR, name))
    return json.loads(f.read())


def get_samples():
    """
    Read the samples and return it as a dict where the filename is the key
    """
    samples = {}
    for f in glob.glob(DIR + '/*.json'):
        name = os.path.basename(f)[:-(len(".json"))]
        samples[name] = get_sample(name)
    return samples

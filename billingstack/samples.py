# -*- encoding: utf-8 -*-
#
# Author: Endre Karlson <endre.karlson@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import glob
import os.path

from billingstack.openstack.common import jsonutils as json


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

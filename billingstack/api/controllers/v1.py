# -*- encoding: utf-8 -*-
#
# Copyright © 2012 Woorea Solutions, S.L
#
# Author: Luis Gervaso <luis@woorea.es>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from pecan.rest import RestController

import wsmeext.pecan as wsme_pecan
from wsme.types import Base, text

class Merchant(Base):
	merchant_id = text
	
class MerchantsController(RestController):
	"""Merchants controller"""
	
	@wsme_pecan.wsexpose(Merchant, unicode)
	def get_one(self, merchant_id):
		"""Get merchant details
		
		:param merchant_id: The UUID of the merchant
		"""
		return Merchant()
		
class V1Controller(object):
	"""Version 1 API controller."""
	
	merchants = MerchantsController()
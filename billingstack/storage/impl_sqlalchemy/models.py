# Copyright 2012 Bouvet ASA
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
from sqlalchemy import (Column, DateTime, String, Text, Integer, ForeignKey,
                        Enum, Boolean, Unicode)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from billingstack.openstack.common import log as logging
from billingstack.openstack.common import timeutils
from billingstack.openstack.common.db.sqlalchemy.models import ModelBase
from billingstack.openstack.common.uuidutils import generate_uuid
from billingstack.storage.impl_sqlalchemy.types import UUID
from sqlalchemy.ext.declarative import declarative_base

LOG = logging.getLogger(__name__)


class ModelBase(ModelBase):
    id = Column(UUID, default=generate_uuid, primary_key=True)
    created_at = Column(DateTime, default=timeutils.utcnow)
    updated_at = Column(DateTime, onupdate=timeutils.utcnow)


ModelBase = declarative_base(cls=ModelBase)


class Test(ModelBase):
    __tablename__ = 'test'

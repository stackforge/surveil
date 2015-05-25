# Copyright 2015 - Savoir-Faire Linux inc.
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

import pecan
import wsmeext.pecan as wsme_pecan
from pecan import rest

from surveil.api.datamodel.logs import alert
from surveil.api.handlers.logs import alert_handler
from surveil.common import util


class AlertsController(rest.RestController):

    @util.policy_enforce(['authenticated'])
    @wsme_pecan.wsexpose([alert.Alert])
    def get_all(self):
        """Returns all alerts"""
        handler = alert_handler.AlertHandler(pecan.request)
        alerts = handler.get_all()
        return alerts
# Copyright 2014 - Savoir-Faire Linux inc.
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
from pecan import rest
import wsmeext.pecan as wsme_pecan

from surveil.api.controllers.v2 import logs
from surveil.api.controllers.v2.status import metrics
from surveil.api.datamodel.status import live_host
from surveil.api.datamodel.status import live_query
from surveil.api.datamodel.status import live_service
from surveil.api.handlers.status import live_host_handler
from surveil.api.handlers.status import live_service_handler


class HostsController(rest.RestController):

    @wsme_pecan.wsexpose([live_host.LiveHost])
    def get_all(self):
        """Returns all hosts."""
        handler = live_host_handler.HostHandler(pecan.request)
        hosts = handler.get_all()
        return hosts

    @wsme_pecan.wsexpose([live_host.LiveHost], body=live_query.LiveQuery)
    def post(self, query):
        """Given a LiveQuery, returns all matching hosts."""
        handler = live_host_handler.HostHandler(pecan.request)
        hosts = handler.get_all(live_query=query)
        return hosts

    @pecan.expose()
    def _lookup(self, host_name, *remainder):
        return HostController(host_name), remainder


class ConfigController(rest.RestController):

    @pecan.expose()
    def get_all(self):
        """Returns config from a specific host."""
        return "Dump CONFIG"


class HostServicesController(rest.RestController):

    @pecan.expose()
    def _lookup(self, service_name, *remainder):
        return HostServiceController(service_name), remainder


class HostServiceController(rest.RestController):

    def __init__(self, service_name):
        pecan.request.context['service_name'] = service_name
        self.service_name = service_name

    @wsme_pecan.wsexpose(live_service.LiveService)
    def get(self):
        """Returns a specific host service."""
        handler = live_service_handler.ServiceHandler(pecan.request)
        service = handler.get(
            pecan.request.context['host_name'],
            self.service_name
        )
        return service


class HostController(rest.RestController):

    services = HostServicesController()
    # See init for controller creation. We need host_name to instanciate it
    # externalcommands = ExternalCommandsController()
    # config = config.ConfigController()
    events = logs.LogsController()
    metrics = metrics.MetricsController()

    def __init__(self, host_name):
        pecan.request.context['host_name'] = host_name
        self.host_name = host_name

    @wsme_pecan.wsexpose(live_host.LiveHost)
    def get(self):
        """Returns a specific host."""
        handler = live_host_handler.HostHandler(pecan.request)
        host = handler.get(self.host_name)
        return host
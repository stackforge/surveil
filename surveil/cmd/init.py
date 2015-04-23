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

"""Script to reinitialize surveil."""

import subprocess

import pymongo
import surveilclient.client as sc

from surveil.api import config


def main():
    # Create a basic config in mongodb
    mongo = pymongo.MongoClient(config.surveil_api_config['mongodb_uri'])

    # Drop the current shinken config
    mongo.drop_database('shinken')

    # Load the shinken packs
    subprocess.call(
        [
            "surveil-pack-upload",
            "--mongo-url=mongo",
            "--mongo-port=27017",
            "/packs/linux-keystone/",
        ]
    )

    subprocess.call(
        [
            "surveil-pack-upload",
            "--mongo-url=mongo",
            "--mongo-port=27017",
            "/packs/linux-glance/",
        ]
    )

    subprocess.call(
        [
            "surveil-pack-upload",
            "--mongo-url=mongo",
            "--mongo-port=27017",
            "/packs/generic-host/",
        ]
    )

    # Reload the surveil config
    cli_surveil = sc.Client('http://localhost:8080/v2', version='2_0')

    cli_surveil.config.hosts.create(
        use="generic-host",
        contact_groups="admins",
        host_name="arbiter",
        address="localhost"
    )

    cli_surveil.config.services.create(
        check_command="check_tcp!7760",
        check_interval="5",
        check_period="24x7",
        contact_groups="admins",
        contacts="admin",
        host_name="ws-arbiter",
        max_check_attempts="5",
        notification_interval="30",
        notification_period="24x7",
        retry_interval="3",
        service_description="check-ws-arbiter"
    )

    cli_surveil.config.hosts.create(
        host_name='test_keystone',
        use='linux-keystone',
        address='127.0.0.1',
        custom_fields={
            "_OS_AUTH_URL": "bla",
            "_OS_USERNAME": "bli",
            "_OS_PASSWORD": "blo",
            "_OS_TENANT":   "blu",
            "_KS_SERVICES": "bly",
            "parents": "localhost"
        }
    )

    cli_surveil.config.reload_config()

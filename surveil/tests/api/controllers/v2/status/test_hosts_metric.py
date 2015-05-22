# Copyright 2015 - Savoir-Faire Linux inc.
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

import json

import httpretty

from surveil.tests.api import functionalTest


class TestHostMetric(functionalTest.FunctionalTest):
    def setUp(self):
        super(TestHostMetric, self).setUp()
        self.influxdb_response = json.dumps({
            "results": [
                {
                    "series": [
                        {"name": "metric_load1",
                         "tags": {"host_name": "srv-monitoring-01",
                                  "service_description": "load",
                                  },
                         "columns": [
                             "time",
                             "critical",
                             "min",
                             "value",
                             "warning"
                         ],
                         "values": [
                             ["2015-04-19T01:09:24Z",
                              "30",
                              "0",
                              "0.60",
                              "15"]
                         ]},
                        {"name": "metric_load1",
                         "tags": {"host_name": "test_keystone",
                                  "service_description": "unload"},
                         "columns": [
                             "time",
                             "critical",
                             "min",
                             "value",
                             "warning"
                         ],
                         "values": [
                             ["2015-04-19T01:09:23Z",
                              "60",
                              "0",
                              "1.5",
                              "20"]
                         ]},
                        {"name": "metric_load1",
                         "tags": {"host_name": "ws-arbiter",
                                  },
                         "columns": [
                             "time",
                             "critical",
                             "min",
                             "value",
                             "warning"
                         ],
                         "values": [
                             ["2015-04-19T01:09:24Z",
                              "20",
                              "0",
                              "6",
                              "10"],
                         ]}
                    ]
                }
            ]
        })

    @httpretty.activate
    def test_get_metric_hosts(self):
        httpretty.register_uri(httpretty.GET,
                               "http://influxdb:8086/query",
                               body=self.influxdb_response)

        response = self.get("/v2/status/hosts/srv-monitoring-01/metrics/load1")

        expected = {
            "metric_name": "load1",
            "min": "0",
            "critical": "30",
            "warning": "15",
            "value": "0.6"
        }

        self.assert_count_equal_backport(
            json.loads(response.body.decode()),
            expected)
        self.assertEqual(
            httpretty.last_request().querystring['q'],
            ["SELECT * FROM metric_load1 "
             "WHERE host_name= 'srv-monitoring-01' "
             "GROUP BY service_description "
             "ORDER BY time DESC LIMIT 1"]
        )

    @httpretty.activate
    def test_time_hosts(self):
        self.influxdb_response = json.dumps({
            "results": [
                {"series": [
                    {"name": "metric_load1",
                     "tags": {"host_name": "srv-monitoring-01",
                              "service_description": "load"},
                     "columns": ["time",
                                 "critical",
                                 "min",
                                 "value",
                                 "warning",
                                 ],
                     "values": [["2015-04-19T01:09:24Z",
                                 "30",
                                 "0",
                                 "0.6",
                                 "15"],
                                ["2015-04-19T01:09:25Z",
                                 "40",
                                 "4",
                                 "10",
                                 "10"]]}]}]

        })
        httpretty.register_uri(httpretty.GET,
                               "http://influxdb:8086/query",
                               body=self.influxdb_response)

        time = {'begin': '2015-04-19T00:09:24Z',
                'end': '2015-04-19T02:09:25Z'}

        response = self.post_json("/v2/status/hosts/srv-monitoring-01/"
                                  "services/load/metrics/load1",
                                  params=time)

        expected = [{"metric_name": 'load1',
                     "min": "0",
                     "critical": "30",
                     "warning": "15",
                     "value": "0.6"
                     },
                    {"metric_name": 'load1',
                     "min": "4",
                     "critical": "40",
                     "warning": "10",
                     "value": "10"
                     }]

        self.assert_count_equal_backport(
            json.loads(response.body.decode()),
            expected)
        self.assertEqual(
            httpretty.last_request().querystring['q'],
            ["SELECT * FROM metric_load1 "
             "WHERE time >= '2015-04-19T00:09:24Z' "
             "AND time <= '2015-04-19T02:09:25Z' "
             "AND host_name ='srv-monitoring-01' "
             "AND service_description ='load' "
             "ORDER BY time DESC"
             ]
        )

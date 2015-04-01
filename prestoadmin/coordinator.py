# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Module for the presto coordinator's configuration.
Loads and validates the coordinator.json file and creates the files needed
to deploy on the presto cluster
"""

import configuration
import configure
import copy
from fabric.api import env
import prestoadmin

CONFIG_PATH = prestoadmin.main_dir + "/resources/coordinator.json"
TMP_OUTPUT_DIR = configure.TMP_CONF_DIR + "/coordinator"
DEFAULT_PROPERTIES = {"node.properties": {"node.environment": "presto",
                                          "node.data-dir": "/var/lib/presto"
                                                           "/data"},
                      "jvm.config": ["-server",
                                     "-Xmx1G",
                                     "-XX:+UseConcMarkSweepGC",
                                     "-XX:+ExplicitGCInvokesConcurrent",
                                     "-XX:+CMSClassUnloadingEnabled",
                                     "-XX:+AggressiveOpts",
                                     "-XX:+HeapDumpOnOutOfMemoryError",
                                     "-XX:OnOutOfMemoryError=kill -9 %p",
                                     "-XX:ReservedCodeCacheSize=150M"],
                      "config.properties": {"coordinator": "true",
                                            "discovery-server.enabled": "true",
                                            "http-server.http.port": 8080,
                                            "task.max-memory": "1GB",
                                            "query.queue-config-file": ""},
                      }


def get_conf():
    conf = configure.validate_types(_get_conf_from_file())
    defaults = build_defaults()
    configuration.fill_defaults(conf, defaults)
    validate(conf)
    return conf


def _get_conf_from_file():
    return configuration.get_conf_from_file(CONFIG_PATH)


def build_defaults():
    conf = copy.deepcopy(DEFAULT_PROPERTIES)
    coordinator = env.roledefs['coordinator']
    workers = env.roledefs['workers']
    if coordinator in workers:
        conf["config.properties"]["node-scheduler."
                                  "include-coordinator"] = "true"
    conf["config.properties"]["discovery.uri"] = "http://" + coordinator \
                                                 + ":8080"

    validate(conf)
    return conf


def validate(conf):
    configure.validate(conf)
    if conf["config.properties"]["coordinator"] is not "true":
        raise configuration.ConfigurationError("Coordinator cannot be false "
                                               "in the coordinator's "
                                               "config.properties")
    return conf


def write_tmp_files(conf):
    configure.write_conf_to_tmp(conf, TMP_OUTPUT_DIR)
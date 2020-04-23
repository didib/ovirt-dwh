#
# ovirt-engine-setup -- ovirt engine setup
# Copyright (C) 2020 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""grafana connection plugin."""

# Not really verifying connection right now - we do not need it, as we
# do not do anything on the database. Keeping the name for compatibility
# with other databases. Only set defaults for now.

import gettext

from otopi import plugin
from otopi import util

from ovirt_engine_setup.grafana_dwh import constants as ogdwhcons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-dwh')


@util.export
class Plugin(plugin.PluginBase):
    """Grafana connection plugin."""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment.setdefault(
            ogdwhcons.GrafanaDBEnv.USER,
            None
        )
        self.environment.setdefault(
            ogdwhcons.GrafanaDBEnv.PASSWORD,
            None
        )


# vim: expandtab tabstop=4 shiftwidth=4

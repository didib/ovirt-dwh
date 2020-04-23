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


"""Local grafana Postgres plugin."""


import gettext

from otopi import plugin
from otopi import util

from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.dwh import constants as odwhcons
from ovirt_engine_setup.grafana_dwh import constants as ogdwhcons
from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.engine_common import postgres

from ovirt_setup_lib import dialog


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-dwh')


@util.export
class Plugin(plugin.PluginBase):
    """Local grafana Postgres plugin."""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)
        self._provisioning = postgres.Provisioning(
            plugin=self,
            dbenvkeys=ogdwhcons.Const.GRAFANA_DB_ENV_KEYS,
            defaults=ogdwhcons.Const.DEFAULT_GRAFANA_DB_ENV_KEYS,
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment.setdefault(
            odwhcons.ProvisioningEnv.POSTGRES_PROVISIONING_ENABLED,
            None
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_SETUP,
        after=(
            odwhcons.Stages.DB_CONNECTION_SETUP,
        ),
        condition=lambda self: (
            not self.environment[
                osetupcons.CoreEnv.DEVELOPER_MODE
            ] and
            self.environment[
                odwhcons.DBEnv.NEW_DATABASE
            ]
        ),
    )
    def _setup(self):
        self._provisioning.detectCommands()

    @plugin.event(
        stage=plugin.Stages.STAGE_CUSTOMIZATION,
        before=(
            oengcommcons.Stages.DIALOG_TITLES_E_DATABASE,
            ogdwhcons.Stages.DB_GRAFANA_CONNECTION_CUSTOMIZATION,
        ),
        after=(
            oengcommcons.Stages.DIALOG_TITLES_S_DATABASE,
            odwhcons.Stages.DB_PROVISIONING,
        ),
        condition=lambda self: self.environment[
            odwhcons.ProvisioningEnv.POSTGRES_PROVISIONING_ENABLED
        ],
    )
    def _customization(self):
        self._provisioning.applyEnvironment()

    @plugin.event(
        stage=plugin.Stages.STAGE_VALIDATION,
        condition=lambda self: self.environment[
            odwhcons.ProvisioningEnv.POSTGRES_PROVISIONING_ENABLED
        ],
    )
    def _validation(self):
        self._provisioning.validate()

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        after=(
            odwhcons.Stages.DB_SCHEMA,
        ),
        condition=lambda self: self.environment[
            odwhcons.ProvisioningEnv.POSTGRES_PROVISIONING_ENABLED
        ],
    )
    def _misc(self):
        self._provisioning.createUser()
        self._provisioning.addPgHbaDatabaseAccess()
        self._provisioning.grantReadOnlyAccessToUser()

    @plugin.event(
        stage=plugin.Stages.STAGE_CLOSEUP,
        before=(
            osetupcons.Stages.DIALOG_TITLES_E_SUMMARY,
        ),
        after=(
            osetupcons.Stages.DIALOG_TITLES_S_SUMMARY,
        ),
        condition=lambda self: self._provisioning.databaseRenamed,
    )
    def _closeup(self):
        self.dialog.note(
            text=_(
                'ovirt grafana database resources:\n'
                '    Database name:      {database}\n'
                '    Database user name: {user}\n'
            ).format(
                database=self.environment[
                    ogdwhcons.GrafanaDBEnv.DATABASE
                ],
                user=self.environment[
                    ogdwhcons.GrafanaDBEnv.USER
                ],
            )
        )

# vim: expandtab tabstop=4 shiftwidth=4

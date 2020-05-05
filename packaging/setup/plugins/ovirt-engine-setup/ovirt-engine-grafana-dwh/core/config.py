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


import gettext
import random
import string


from otopi import constants as otopicons
from otopi import filetransaction
from otopi import util
from otopi import plugin

from ovirt_engine import util as outil

from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.grafana_dwh import constants as ogdwhcons
from ovirt_setup_lib import dialog


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-dwh')


@util.export
class Plugin(plugin.PluginBase):

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @staticmethod
    def _generatePassword():
        return ''.join([
            random.SystemRandom().choice(
                string.ascii_letters +
                string.digits
            ) for i in range(22)
        ])

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment.setdefault(
            ogdwhcons.ConfigEnv.ADMIN_PASSWORD,
            None
        )
        self.environment.setdefault(
            ogdwhcons.ConfigEnv.CONF_SECRET_KEY,
            self._generatePassword()
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_CUSTOMIZATION,
        before=(
            osetupcons.Stages.DIALOG_TITLES_E_MISC,
        ),
        after=(
            osetupcons.Stages.DIALOG_TITLES_S_MISC,
        ),
        condition=lambda self: (
            self.environment[ogdwhcons.ConfigEnv.ADMIN_PASSWORD] is None and
            self.environment[ogdwhcons.CoreEnv.ENABLE] and
            self.environment[ogdwhcons.ConfigEnv.NEW_DATABASE]
        ),
    )
    def _customization_admin_password(self):
        password = None
        if self.environment[oenginecons.ConfigEnv.ADMIN_PASSWORD]:
            use_engine_admin_password = dialog.queryBoolean(
                dialog=self.dialog,
                name='GRAFANA_USE_ENGINE_ADMIN_PASSWORD',
                note=_(
                    'Use Engine admin password as initial Grafana admin '
                    'password (@VALUES@) [@DEFAULT@]: '
                ),
                prompt=True,
                default=True
            )
            if use_engine_admin_password:
                password = self.environment[
                    oenginecons.ConfigEnv.ADMIN_PASSWORD
                ]
        if password is None:
            password = dialog.queryPassword(
                dialog=self.dialog,
                logger=self.logger,
                env=self.environment,
                key=ogdwhcons.ConfigEnv.ADMIN_PASSWORD,
                note=_(
                    'Grafana admin password: '
                ),
            )
        self.environment[ogdwhcons.ConfigEnv.ADMIN_PASSWORD] = password

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        condition=lambda self: (
            self.environment[ogdwhcons.CoreEnv.ENABLE] and
            self.environment[ogdwhcons.ConfigEnv.NEW_DATABASE]
        ),
    )
    def _misc_grafana_config(self):
        uninstall_files = []
        self.environment[
            osetupcons.CoreEnv.REGISTER_UNINSTALL_GROUPS
        ].addFiles(
            group='ovirt_grafana_files',
            fileList=uninstall_files,
        )
        self.environment[otopicons.CoreEnv.MAIN_TRANSACTION].append(
            filetransaction.FileTransaction(
                name=(
                    ogdwhcons.FileLocations.
                    GRAFANA_CONFIG_FILE
                ),
                mode=0o640,
                owner='root',
                group='grafana',
                enforcePermissions=True,
                content=outil.processTemplate(
                    template=(
                        ogdwhcons.FileLocations.
                        GRAFANA_CONFIG_FILE_TEMPLATE
                    ),
                    subst={
                        '@ADMIN_PASSWORD@': self.environment[
                            ogdwhcons.ConfigEnv.ADMIN_PASSWORD
                        ],
                        '@PROVISIONING@': (
                            ogdwhcons.FileLocations.
                            GRAFANA_PROVISIONING_CONFIGURATION
                        ),
                        '@GRAFANA_PORT@': self.environment[
                            ogdwhcons.ConfigEnv.GRAFANA_PORT
                        ],
                        '@SECRET_KEY@': self.environment[
                            ogdwhcons.ConfigEnv.CONF_SECRET_KEY
                        ],
                        '@GRAFANA_STATE_DIR@': (
                            ogdwhcons.FileLocations.GRAFANA_STATE_DIR
                        ),
                        '@GRAFANA_DB@': (
                            ogdwhcons.FileLocations.GRAFANA_DB
                        ),
                    },
                ),
                modifiedList=uninstall_files,
            )
        )


# vim: expandtab tabstop=4 shiftwidth=4

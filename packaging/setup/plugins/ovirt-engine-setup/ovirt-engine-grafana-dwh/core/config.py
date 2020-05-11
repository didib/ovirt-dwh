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


import atexit
import gettext
import os
import random
import string
import tempfile


from otopi import constants as otopicons
from otopi import filetransaction
from otopi import util
from otopi import plugin

from ovirt_engine import configfile
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
        self._sso_config = None
        self._grafana_fqdn = None

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
        stage=plugin.Stages.STAGE_CUSTOMIZATION,
        before=(
            osetupcons.Stages.DIALOG_TITLES_E_MISC,
        ),
        after=(
            osetupcons.Stages.DIALOG_TITLES_S_MISC,
        ),
        condition=lambda self: (
            self.environment[ogdwhcons.CoreEnv.ENABLE] and
            self.environment[ogdwhcons.ConfigEnv.NEW_DATABASE]
        ),
    )
    def _customization_sso(self):
        sso_client_tool = '/usr/bin/ovirt-register-sso-client-tool'
        if not os.path.exists(sso_client_tool):
            # TODO: make this optional
            # After grafana supports split config files, have sso in its
            # own file
            raise RuntimeError(_('{tool} is missing').format(sso_client_tool))

        # We should already have ENGINE_FQDN even if remote, because we
        # are in MISC title which is after NETWORK title
        engine_fqdn = self.environment[oenginecons.ConfigEnv.ENGINE_FQDN]

        # TODO: Fix for separate machines
        self._grafana_fqdn = engine_fqdn
        

        fd, tmpconf = tempfile.mkstemp()
        atexit.register(os.unlink, tmpconf)

        sso_client_tool_cmd = (
            '{tool} '
            '--callback-prefix-url=https://{grafana_fqdn}/ovirt-engine-grafana/ '
            '--client-ca-location={ca_pem} '
            '--client-id={client_id} '
            '--encrypted-userinfo=false '
            '--conf-file-name={tmpconf}'
        ).format(
            tool=sso_client_tool,
            grafana_fqdn=self._grafana_fqdn,
            ca_pem=oenginecons.FileLocations.OVIRT_ENGINE_PKI_ENGINE_CA_CERT,
            client_id=ogdwhcons.Const.OVIRT_GRAFANA_SSO_CLIENT_ID,
            tmpconf=tmpconf,
        )
        if self.environment[oenginecons.CoreEnv.ENABLE]:
            self.execute(sso_client_tool_cmd.split(' '))
        else:
            # TODO: do this with remote_engine
            dialog.queryString(
                name='PROMPT_GRAFANA_REMOTE_ENGINE_SSO',
                note=_(
                    'Please run the following command on the engine machine '
                    '{engine_fqdn}:\n'
                    '{cmd}\n'
                    'Then copy the file {tmpconf} from the engine machine to '
                    'this machine, and press Enter to continue: '
                ).format(
                    engine_fqdn=engine_fqdn,
                    cmd=sso_client_tool_cmd,
                    tmpconf=tmpconf,
                ),
                prompt=True,
                default='y',  # Allow Enter without any value
            )
        self._sso_config = configfile.ConfigFile([tmpconf])
        self.environment[
            otopicons.CoreEnv.LOG_FILTER
        ].append(
            self._sso_config.get(
                'SSO_CLIENT_SECRET'
            )
        )

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
                        '@OVIRT_GRAFANA_SSO_CLIENT_ID@': self._sso_config.get(
                            'SSO_CLIENT_ID'
                        ),
                        '@OVIRT_GRAFANA_SSO_CLIENT_SECRET@': self._sso_config.get(
                            'SSO_CLIENT_SECRET'
                        ),
                        '@ENGINE_SSO_AUTH_URL@': (
                            'https://{fqdn}/ovirt-engine/sso'.format(
                                fqdn=self.environment[
                                    oenginecons.ConfigEnv.ENGINE_FQDN
                                ],
                            )
                        ),
                        '@ROOT_URL@': (
                            'https://{fqdn}/ovirt-engine-grafana/'.format(
                                fqdn=self._grafana_fqdn,
                            )
                        ),
                    },
                ),
                modifiedList=uninstall_files,
            )
        )


# vim: expandtab tabstop=4 shiftwidth=4

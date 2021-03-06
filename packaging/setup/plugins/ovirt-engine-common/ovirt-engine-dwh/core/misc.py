#
# ovirt-engine-setup -- ovirt engine setup
# Copyright (C) 2013-2015 Red Hat, Inc.
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


from otopi import util
from otopi import plugin


from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.dwh import constants as odwhcons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-dwh')


@util.export
class Plugin(plugin.PluginBase):

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment.setdefault(odwhcons.CoreEnv.ENABLE, None)
        self.environment.setdefault(oenginecons.CoreEnv.ENABLE, None)

    @plugin.event(
        stage=plugin.Stages.STAGE_SETUP,
    )
    def _setup(self):
        self.environment[
            osetupcons.CoreEnv.REGISTER_UNINSTALL_GROUPS
        ].createGroup(
            group='ovirt_dwh_files',
            description='DWH files',
            optional=True,
        )
        self.environment[
            osetupcons.CoreEnv.SETUP_ATTRS_MODULES
        ].append(odwhcons)
        self.logger.debug(
            'dwh version: %s-%s (%s)\n',
            odwhcons.Const.PACKAGE_NAME,
            odwhcons.Const.PACKAGE_VERSION,
            odwhcons.Const.DISPLAY_VERSION,
        )


# vim: expandtab tabstop=4 shiftwidth=4

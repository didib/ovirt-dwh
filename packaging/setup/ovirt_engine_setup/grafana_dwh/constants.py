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


"""Grafana DWH Constants."""


import os
import gettext


from otopi import util

from ovirt_engine_setup.constants import classproperty
from ovirt_engine_setup.constants import osetupattrsclass
from ovirt_engine_setup.constants import osetupattrs
from ovirt_engine_setup.engine_common import constants as oengcommcons


from . import config


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-dwh')


DEK = oengcommcons.DBEnvKeysConst


@util.export
@util.codegen
class Const(object):
    SERVICE_NAME = 'grafana-server'
    OVIRT_ENGINE_GRAFANA_DWH_SETUP_PACKAGE_NAME = \
        'ovirt-engine-dwh-grafana-integration-setup'

    @classproperty
    def DWH_DB_ENV_KEYS(self):
        return {
            DEK.HOST: DWHDBEnv.HOST,
            DEK.PORT: DWHDBEnv.PORT,
            DEK.SECURED: DWHDBEnv.SECURED,
            DEK.HOST_VALIDATION: DWHDBEnv.SECURED_HOST_VALIDATION,
            DEK.USER: DWHDBEnv.USER,
            DEK.PASSWORD: DWHDBEnv.PASSWORD,
            DEK.DATABASE: DWHDBEnv.DATABASE,
            DEK.CONNECTION: DWHDBEnv.CONNECTION,
            DEK.PGPASSFILE: DWHDBEnv.PGPASS_FILE,
            DEK.NEW_DATABASE: DWHDBEnv.NEW_DATABASE,
            DEK.DUMPER: DWHDBEnv.DUMPER,
            DEK.FILTER: DWHDBEnv.FILTER,
            DEK.RESTORE_JOBS: DWHDBEnv.RESTORE_JOBS,
        }

    @classproperty
    def DEFAULT_DWH_DB_ENV_KEYS(self):
        return {
            DEK.HOST: DWHDefaults.DEFAULT_DB_HOST,
            DEK.PORT: DWHDefaults.DEFAULT_DB_PORT,
            DEK.SECURED: DWHDefaults.DEFAULT_DB_SECURED,
            DEK.HOST_VALIDATION:
                DWHDefaults.DEFAULT_DB_SECURED_HOST_VALIDATION,
            DEK.USER: DWHDefaults.DEFAULT_DB_USER,
            DEK.PASSWORD: DWHDefaults.DEFAULT_DB_PASSWORD,
            DEK.DATABASE: DWHDefaults.DEFAULT_DB_DATABASE,
        }


@util.export
@util.codegen
class Defaults(object):
    DEFAULT_ADDITIONAL_PACKAGES = (
        'grafana'
        ',grafana-postgres',
    )


@util.export
@util.codegen
class DWHDefaults(object):
    DEFAULT_DB_HOST = ''
    DEFAULT_DB_PORT = 5432
    DEFAULT_DB_DATABASE = 'ovirt_engine_history'
    DEFAULT_DB_USER = 'ovirt_engine_history'
    DEFAULT_DB_PASSWORD = ''
    DEFAULT_DB_SECURED = False
    DEFAULT_DB_SECURED_HOST_VALIDATION = False


@util.export
@util.codegen
class FileLocations(object):
    GRAFANA_SYSCONF_DIR = config.GRAFANA_SYSCONF_DIR
    GRAFANA_STATE_DIR = config.GRAFANA_STATE_DIR
    GRAFANA_DATA_DIR = config.GRAFANA_DATA_DIR
    PKG_DATA_DIR = config.PKG_DATA_DIR

    GRAFANA_CONFIG_FILE = os.path.join(
        GRAFANA_SYSCONF_DIR,
        'grafana.ini',
    )
    GRAFANA_CONFIG_FILE_TEMPLATE = os.path.join(
        PKG_DATA_DIR,
        'grafana.ini.in',
    )


@util.export
class Stages(object):
    CORE_ENABLE = 'osetup.grafana.core.enable'


@util.export
@util.codegen
@osetupattrsclass
class CoreEnv(object):

    @osetupattrs(
        answerfile=True,
        postinstallfile=True,
        summary=True,
        reconfigurable=True,
        description=_('Grafana integration'),
    )
    def ENABLE(self):
        return 'OVESETUP_GRAFANA_CORE/enable'


@util.export
@util.codegen
@osetupattrsclass
class ConfigEnv(object):
    GRAFANA_SERVICE_STOP_NEEDED = \
        'OVESETUP_GRAFANA_CONFIG/grafanaServiceStopNeeded'

    @osetupattrs(
        answerfile=True,
        is_secret=True,
    )
    def ADMIN_PASSWORD(self):
        return 'OVESETUP_GRAFANA_CONFIG/adminPassword'


@util.export
@util.codegen
@osetupattrsclass
class DWHDBEnv(object):
    """Sync with ovirt-dwh"""

    @osetupattrs(
        answerfile=True,
        summary=True,
        description=_('DWH database host'),
    )
    def HOST(self):
        return 'OVESETUP_DWH_DB/host'

    @osetupattrs(
        answerfile=True,
        summary=True,
        description=_('DWH database port'),
    )
    def PORT(self):
        return 'OVESETUP_DWH_DB/port'

    @osetupattrs(
        answerfile=True,
        summary=True,
        description=_('DWH database secured connection'),
    )
    def SECURED(self):
        return 'OVESETUP_DWH_DB/secured'

    @osetupattrs(
        answerfile=True,
        summary=True,
        description=_('DWH database host name validation'),
    )
    def SECURED_HOST_VALIDATION(self):
        return 'OVESETUP_DWH_DB/securedHostValidation'

    @osetupattrs(
        answerfile=True,
        summary=True,
        description=_('DWH database name'),
    )
    def DATABASE(self):
        return 'OVESETUP_DWH_DB/database'

    @osetupattrs(
        answerfile=True,
        summary=True,
        description=_('DWH database user name'),
    )
    def USER(self):
        return 'OVESETUP_DWH_DB/user'

    @osetupattrs(
        answerfile=True,
    )
    def PASSWORD(self):
        return 'OVESETUP_DWH_DB/password'

    CONNECTION = 'OVESETUP_DWH_DB/connection'
    STATEMENT = 'OVESETUP_DWH_DB/statement'
    PGPASS_FILE = 'OVESETUP_DWH_DB/pgPassFile'
    NEW_DATABASE = 'OVESETUP_DWH_DB/newDatabase'

    @osetupattrs(
        answerfile=True,
    )
    def DUMPER(self):
        return 'OVESETUP_DWH_DB/dumper'

    @osetupattrs(
        answerfile=True,
    )
    def FILTER(self):
        return 'OVESETUP_DWH_DB/filter'

    @osetupattrs(
        answerfile=True,
    )
    def RESTORE_JOBS(self):
        return 'OVESETUP_DWH_DB/restoreJobs'


@util.export
@util.codegen
@osetupattrsclass
class RemoveEnv(object):
    pass


@util.export
@util.codegen
@osetupattrsclass
class RPMDistroEnv(object):
    ADDITIONAL_PACKAGES = 'OVESETUP_GRAFANA_RPMDISTRO/additionalPackages'
    PACKAGES_SETUP = 'OVESETUP_GRAFANA_RPMDISRO_PACKAGES_SETUP'


# vim: expandtab tabstop=4 shiftwidth=4

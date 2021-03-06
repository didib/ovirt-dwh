#
# ovirt-engine-setup -- ovirt engine setup
# Copyright (C) 2013-2014 Red Hat, Inc.
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


from otopi import util


from . import check_etl
from . import single_etl
from . import config
from . import misc
from . import remote_engine
from . import scale
from . import service
from . import dwh
from . import dwh_database


@util.export
def createPlugins(context):
    check_etl.Plugin(context=context)
    single_etl.Plugin(context=context)
    config.Plugin(context=context)
    misc.Plugin(context=context)
    remote_engine.Plugin(context=context)
    scale.Plugin(context=context)
    service.Plugin(context=context)
    dwh.Plugin(context=context)
    dwh_database.Plugin(context=context)


# vim: expandtab tabstop=4 shiftwidth=4

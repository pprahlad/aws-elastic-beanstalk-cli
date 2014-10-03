# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.


class Environment():
    def __init__(self, version_label=None, status=None, app_name=None,
                 health=None, id=None, date_updated=None,
                 solution_stack=None, description=None,
                 name=None, date_created=None, tier=None,
                 cname=None):

        self.version_label = version_label
        self.status = status
        self.app_name = app_name
        self.health = health
        self.id = id
        self.date_updated = date_updated
        self.solution_stack = solution_stack
        self.description = description
        self.name = name
        self.date_created = date_created
        self.tier = tier
        self.cname = cname
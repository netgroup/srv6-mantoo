#!/bin/bash

#
# Copyright (C) 2017 Stefano Salsano, Pier Luigi Ventre - (CNIT and University of Rome "Tor Vergata")
#
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
#
# Script to update bashrc to change the prompt in mininet with the node name 
#
# @author Stefano Salsano <stefano.salsano@uniroma2.it>
# @author Pier Luigi Ventre <pier.luigi.ventre@uniroma2.it>
#

if [ -f root_bash_rc ]; then
    sudo cp root_bash_rc /root/.bashrc
else
    echo 'root_bash_rc NOT FOUND - nothing has been configured'
fi

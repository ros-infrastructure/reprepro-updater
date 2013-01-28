# Software License Agreement (BSD License)
#
# Copyright (c) 2012, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


class ConfParameters(object):

    def __init__(self, distros, architectures, rosdistros):
        self.distros = distros
        self.architectures = architectures
        self.rosdistros = rosdistros


    
        

class IncomingFile(object):
    def __init__(self, distros):
        self.distros = distros

        self.standard_snippet = """Name: %(distro)s
IncomingDir: queue/%(distro)s
TempDir: tmp
Allow: %(distro)s

"""

        self.all_snippet = """Name: all
IncomingDir: queue/all
TempDir: tmp
Allow: %(distros)s
Cleanup: on_deny on_error
Options: multiple_distributions

"""

    def generate_file_contents(self):
        out = ''
        for d in self.distros:
            out += self.standard_snippet % {'distro': d}
        out += self.all_snippet % {'distros': ' '.join(self.distros) }
        return out


class DistributionsFile(object):
    def __init__(self, distros, arches, repo_key, update_objects):
        self.distros = distros
        self.arches = arches
        self.repo_key = repo_key
        self.update_objects = update_objects

        self.standard_snippet = """Origin: ROS
Label: ROS %(distro)s
Codename: %(distro)s
Suite: %(distro)s
Architectures: %(archs)s
Components: main
Description: ROS %(distro)s Debian Repository
SignWith: %(repo_key)s
Update: %(update_rule)s

"""

    #TODO remove arch from arguments add to for loop?
    def generate_file_contents(self, rosdistro, arch):
        out = ''

        # all distros must be listed in the distributions file for reprepro to be happy
        for dist in self.distros:
            if self.update_objects:
                update_rule = ' '.join(self.update_objects.get_update_names(rosdistro, dist, arch) )
            else:
                update_rule = ''
            d = {'distro': dist, 
                 'archs': ' '.join(self.arches),
                 'repo_key': self.repo_key,
                 'update_rule': update_rule}
            out += self.standard_snippet % d

        return out


class UpdateElement(object):
    def __init__(self, name, method, suites, component, architectures, filter_formula=None):
        self.name = name
        self.method = method
        self.suites = suites
        self.component = component
        self.architectures = architectures
        self.filter_formula = filter_formula


    def generate_update_rule(self, distro, arch):
        if not distro in self.suites:
            return ''
        if not arch in self.architectures:
            return ''
        output = ''
        output += 'Name: %s\n' % self.name
        output += 'Method: %s\n' % self.method
        output += 'Suite: %s\n' % distro
        output += 'Components: %s\n' % self.component
        output += 'Architectures: %s\n' % arch
        if self.filter_formula:
            output += 'FilterFormula: %s' % self.filter_formula
        output += '\n'
        return output

class UpdatesFile(object):
    def __init__(self, rosdistros, distros, arches, repo_key, upstream_method):
        self.rosdistros = rosdistros
        self.upstream_method = upstream_method
        self.distros = distros
        self.arches = arches
        self.repo_key = repo_key
        
        self.update_elements = []

        self.standard_ros_snippet = """Name: ros-%(rosdistro)s-%(distro)s-%(arch)s
Method: %(upstream_method)s
Suite: %(distro)s
Components: main
Architectures: %(arch)s
FilterFormula: Package (%% ros-%(rosdistro)s-*)

"""

    def generate_file_contents(self, rosdistro, distro, arch):
        out = ''
        if self.upstream_method:
            d = {'name': 'ros-%(rosdistro)s-%(distro)s-%(arch)s'%locals(),
                 'upstream_method': self.upstream_method,
                 'rosdistro': rosdistro,
                 'distro': distro,
                 'arch': arch}
            out += self.standard_ros_snippet % d

        for update_element in self.update_elements:
            out += update_element.generate_update_rule(distro, arch)
            
        return out

    def add_update_element(self, update_element):
        self.update_elements.append(update_element)

    def get_update_names(self, rosdistro, suite, arch):
        update_names = []
        # default ros rule
        if self.upstream_method:
            update_names.append('ros-%(rosdistro)s-%(suite)s-%(arch)s'%locals())
        for c in self.update_elements:
            if suite in c.suites:
                if arch in c.architectures:
                    update_names.append(c.name)
        return update_names
    
class ConfGenerator(object):
    """ A Class for genrating the reprepro conf directory.  
    It can generate, the distributions and update rules dynamically for more granular updates. 
    """

    def __init__(self, directory, rosdistros):
        """ Read the basic information """
        self.valid_rosdistros = rosdistros
        

        
        raise NotImplemented


    def generate_distribution(self):
        raise NotImplemented


    def generate_updates(self):
        raise NotImplemented

    def _load_parameters(self, file):
        pass

    def run_update(self):
        pass

        

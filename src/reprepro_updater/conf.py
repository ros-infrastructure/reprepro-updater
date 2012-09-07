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
    def __init__(self, distros, arches, repo_key):
        self.distros = distros
        self.arches = arches
        self.repo_key = repo_key

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

    def generate_file_contents(self, rosdistro, distro, arch):
        out = ''
        d = {'distro': distro, 
             'archs': ' '.join(self.arches),
             'repo_key': self.repo_key,
             'update_rule': 'ros-%s-%s-%s' % (rosdistro, distro, arch)}
        out += self.standard_snippet % d

        return out

class UpdatesFile(object):
    def __init__(self, rosdistros, distros, arches, repo_key, upstream_method):
        self.rosdistros = rosdistros
        self.upstream_method = upstream_method
        self.distros = distros
        self.arches = arches
        self.repo_key = repo_key

        self.standard_snippet = """Name: ros-%(distro)s-%(rosdistro)s-%(arch)s
Method: %(upstream_method)s
Suite: %(rosdistro)s
Components: main
Architectures: %(arch)s
FilterFormula: Package (%% ros-%(rosdistro)s-*)

"""

    def generate_file_contents(self):
        out = ''
        for r in self.rosdistros:
            for dist in self.distros:
                for a in self.arches:
                    d = {'upstream_method': self.upstream_method,
                         'rosdistro': r,
                         'distro': dist,
                         'arch': a}
                    out += self.standard_snippet % d
                    
        return out



class ConfGenerator(object):
    """ A Class for genrating the reprepro conf directory.  
    It can generate, the distributions and update rules dynamically for more granular updates. 
    """

    def __init__(self, directory):
        """ Read the basic information """
        

        
        raise NotImplemented


    def generate_distribution(self):
        raise NotImplemented


    def generate_updates(self):
        raise NotImplemented

    def _load_parameters(self, file):
        pass

    def run_update(self):
        pass

        

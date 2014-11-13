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

from configparser import SafeConfigParser
import os

ALL_DISTROS = ['hardy', 'jaunty', 'karmic', 'lucid', 'maverick',
               'natty', 'oneiric', 'precise', 'quantal', 'raring',
               'saucy', 'trusty',
               'wheezy', 'jessie']
ALL_ARCHES = ['amd64', 'i386', 'armel', 'armhf', 'source']


class ConfParameters(object):

    def __init__(self, repository_path, upstream_config_dir,
                 distros, architectures, signing_key):
        self.repository_path = repository_path
        self.upstream_config_dir = upstream_config_dir
        self.distros = distros
        self.architectures = architectures
        self.signing_key = signing_key
        self.lockfile = os.path.join(repository_path, 'lock')

    def create_distributions_file(self, updates_file):
        print ("self.architectures is ", self.architectures)
        return DistributionsFile(self.distros,
                                 self.architectures,
                                 self.signing_key,
                                 updates_file)

    def distributions_filename(self):
        return os.path.join(self.repository_path, 'conf', 'distributions')

    def incoming_filename(self):
        return os.path.join(self.repository_path, 'conf', 'incoming')

    def updates_filename(self):
        return os.path.join(self.repository_path, 'conf', 'updates')

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
        out += self.all_snippet % {'distros': ' '.join(self.distros)}
        return out

    def create_required_directories(self, repo_root):
        incoming_dirs = ['queue/%s' % d for d in self.distros]
        incoming_dirs.append('queue/all')
        for d in incoming_dirs:
            p = os.path.join(repo_root, d)
            if not os.path.isdir(p):
                print "Incoming dir %s did not exist, creating" % p
                os.makedirs(p)


class DistributionsFile(object):
    def __init__(self, distros, arches, repo_key, update_objects):
        self.distros = distros
        self.arches = arches
        print ("self.arches is ", self.arches)
        self.repo_key = repo_key
        self.update_objects = update_objects

        self.standard_snippet = """Origin: ROS
Label: ROS %(distro)s
Codename: %(distro)s
Suite: %(distro)s
Architectures: %(archs)s
Components: main
Description: ROS %(distro)s Debian Repository
Update: %(update_rule)s
"""

        if self.repo_key:
            self.standard_snippet += """SignWith: %s

""" % self.repo_key
        else:
            self.standard_snippet += """

"""

    # TODO remove arch from arguments add to for loop?
    def generate_file_contents(self, rosdistro, arch):
        out = ''

        # all distros must be listed in the distributions file for reprepro to
        # be happy
        for dist in self.distros:
            if self.update_objects:
                update_rule = ' '.join(self.update_objects.get_update_names(rosdistro, dist, arch) )
            else:
                update_rule = ''
            d = {'distro': dist,
                 'archs': ' '.join(self.arches),
                 'update_rule': update_rule}
            out += self.standard_snippet % d

        return out


class UpdateElement(object):
    def __init__(self, name, method, suites, component, architectures, filter_formula=None, verify_release=None):
        self.name = name
        self.method = method
        self.suites = suites
        self.component = component
        self.architectures = architectures
        self.filter_formula = filter_formula
        self.verify_release = verify_release

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
        if self.verify_release:
            output += 'VerifyRelease: %s' % self.verify_release
        output += '\n'
        return output


class UpdatesFile(object):
    def __init__(self, rosdistros, distros, arches):
        self.rosdistros = rosdistros
        self.distros = distros
        self.arches = arches

        self.update_elements = []

    def generate_file_contents(self, rosdistro, distro, arch):
        out = ''

        for update_element in self.update_elements:
            out += update_element.generate_update_rule(distro, arch)

        return out

    def add_update_element(self, update_element):
        self.update_elements.append(update_element)

    def get_update_names(self, rosdistro, suite, arch):
        update_names = []
        for c in self.update_elements:
            if suite in c.suites:
                if arch in c.architectures:
                    update_names.append(c.name)
        return update_names


class ConfGenerator(object):
    """ A Class for genrating the reprepro conf directory.
    It can generate, the distributions and update rules
    dynamically for more granular updates.
    """

    def __init__(self, config_parameters_object):
        """ Read the basic information """
        self.config_params = config_parameters_object

    def _generate_distribution(self):
        raise NotImplemented

    def _generate_updates(self):
        raise NotImplemented

    def _load_parameters(self, file):
        pass

    def import_from_folder(self, package, folder, invalidate=False):
        """ Import a package from the folder """
        raise NotImplemented

    def run_update(self):
        pass


def load_conf(config_name=None):
    config = SafeConfigParser()
    config_file = os.path.join(
        os.path.expanduser('~'), '.buildfarm', 'reprepro-updater.ini')

    if not config_name:
        config_name = 'DEFAULT'

    if not os.path.exists(config_file):
        print("Warning: config file does not exist: %s" % config_file)
        return None
    config.read(config_file)

    if config_name not in config:
        return None
    config_section = config[config_name]
    if 'repository_path' not in config_section:
        return None

    repo_path = config[config_name]['repository_path']

    def get_config_element(config_section, key, default=None,
                           required=False, expect_list=False):
        if key in config_section:
            if expect_list:
                return config_section[key].split()
            else:
                return str(config_section[key])

        else:
            if not required:
                return default
            raise Exception("Config element %s missing, but required in %s" %
                            (key, config_section))

    return ConfParameters(get_config_element(config_section,
                                             'repository_path',
                                             required=True),
                          get_config_element(config_section,
                                             'upstream_config'),
                          get_config_element(config_section,
                                             'distros',
                                             required=True,
                                             expect_list=True),
                          get_config_element(config_section,
                                             'architectures',
                                             required=True,
                                             expect_list=True),
                          get_config_element(config_section,
                                             'signing_key'),
                          )

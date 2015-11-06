from debian.debian_support import PackageFile
import re
from urllib2 import urlopen
from urllib2 import URLError

def convert_tuples_list_to_dict(tuples_list):
    output = {}
    for (one, two) in tuples_list:
        output[one] = two
    return output


def strip_email(maintainer):
    return re.sub("(.*)<.*>", "\\1", maintainer)


def core_version(version):
    return core_debian_version(core_rosbuild_version(version))


def core_debian_version(version):  # TODO remove hardcoded ubuntu versions here
    return re.sub("(.*)(precise|quantal|saucy|trusty)-\d{8}-\d{4}-\+\d{4}",
                  "\\1", version)


def core_rosbuild_version(version):
    return re.sub("(.*)-s\d{10}~\w*",
                  "\\1",
                  version)


def is_substantial_version_change(v1, v2):
    cv1 = core_version(v1)
    cv2 = core_version(v2)
    # print("core %s %s" % (cv1, cv2))

    return cv1 != cv2


def construct_packages_url(base_url, dist, component, arch):
    return '/'.join([base_url.rstrip('/'), 'dists', dist, component, arch, 'Packages'])


def get_packagefile_from_url(url, name='foo'):
    try:
        fromlines = urlopen(url)
        return PackageFile(name, fromlines)
    except URLError, ex:
        raise RuntimeError("Failed to load from url %s [%s]" % (from_url, ex))

def compute_annoucement(rosdistro, pf_old, pf_new):
    """Compute the difference between to debian Packages files per rosdistro

    Inputs: rosdistro and debian PackageFiles
    Returns: string of difference announcement
    """
    old_packages = {}
    new_packages = {}

    for p in pf_old:
        intermediate = convert_tuples_list_to_dict(p)
        name = intermediate['Package']
        if rosdistro not in name:
            continue
        old_packages[name] = intermediate

    for p in pf_new:
        intermediate = convert_tuples_list_to_dict(p)
        name = intermediate['Package']
        if rosdistro not in name:
            continue
        new_packages[intermediate['Package']] = intermediate

    updated_packages = set()
    removed_packages = set()
    added_packages = set()

    for p in [p for p in new_packages if p in old_packages]:
        if new_packages[p]['Version'] == old_packages[p]['Version']:
            continue
        if is_substantial_version_change(new_packages[p]['Version'],
                                         old_packages[p]['Version']):
            updated_packages.add(p)

    added_packages = set([p for p in new_packages if p not in old_packages])
    removed_packages = set([p for p in old_packages if p not in new_packages])

    maintainers = set()
    for p in added_packages | updated_packages:
        maintainers.add(strip_email(new_packages[p]['Maintainer']).strip())

    class OutputAppender:
        def __init__(self):
            self.value = ""

        def append(self, string_value):
            self.value += string_value + '\n'

    out = OutputAppender()

    out.append("Updates to %s\n" % rosdistro)
    out.append("Added Packages [%s]:\n" % len(added_packages))
    for p in sorted(added_packages):
        out.append(
            " * %s: %s" %
            (p, core_version(new_packages[p]['Version'])))
    out.append("\n")

    out.append("Updated Packages [%s]:\n" % len(updated_packages))
    for p in sorted(updated_packages):
        out.append(
            " * %s: %s -> %s" %
            (p,
             core_version(old_packages[p]['Version']),
             core_version(new_packages[p]['Version'])))
    out.append("\n")

    out.append("Removed Packages [%s]:\n" % len(removed_packages))
    for p in sorted(removed_packages):
        out.append("- %s" % (p))
    out.append("\n")

    out.append(
        "Thanks to all ROS maintainers who make packages"
        " available to the ROS community. The above list "
        "of packages was made possible by the work of the"
        " following maintainers:")
    for maintainer in sorted(maintainers):
        out.append(" * %s" % maintainer)

    return out.value

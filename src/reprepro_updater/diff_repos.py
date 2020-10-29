import re
import sys

from debian.debian_support import PackageFile
from tempfile import NamedTemporaryFile
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve


def convert_tuples_list_to_dict(tuples_list):
    output = {}
    for (one, two) in tuples_list:
        output[one] = two
    return output


def strip_email(maintainer):
    return re.sub("(.*)<.*>", "\\1", maintainer)


def core_version(version):
    # Match DPM 5.6.12: https://www.debian.org/doc/debian-policy/ch-controlfields.html
    result = re.match("\d*:?\d([\d\.\-~0-9]*-\d*|[\d\.~0-9]*)",
                      version)
    if result:
        return result.group()
    return None


def is_substantial_version_change(v1, v2):
    cv1 = core_version(v1)
    cv2 = core_version(v2)
    # print("core %s %s" % (cv1, cv2))

    return cv1 != cv2


def construct_packages_url(base_url, dist, component, arch):
    return '/'.join([base_url.rstrip('/'), 'dists', dist, component, arch, 'Packages'])


def get_packagefile_from_url(url):
    try:
        with NamedTemporaryFile() as temp:
            urlretrieve(url, temp.name)
            package_file = PackageFile('Packages')
    except URLError as ex:
        raise RuntimeError("Failed to load from url %s [%s]" % (url, ex))

    return package_file


def conditional_markdown_package_homepage_link(package, package_file):
    if 'Homepage' in package_file[package]:
        return "[%s](%s)" % (package, package_file[package]['Homepage'])
    else:
        return package


def compute_annoucement(rosdistro, pf_old, pf_new):
    """
    Compute the difference between to debian Packages files per rosdistro.

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

    out = ''

    out += "## Package Updates for %s\n\n" % rosdistro
    out += "### Added Packages [%s]:\n\n" % len(added_packages)
    for p in sorted(added_packages):
        out += " * %s: %s\n" % \
            (conditional_markdown_package_homepage_link(p, new_packages),
            core_version(new_packages[p]['Version']))
    out += "\n"

    out += "### Updated Packages [%s]:\n\n" % len(updated_packages)
    for p in sorted(updated_packages):
        out += " * %s: %s -> %s\n" % \
            (conditional_markdown_package_homepage_link(p, new_packages),
             core_version(old_packages[p]['Version']),
             core_version(new_packages[p]['Version']))
    out += "\n"

    out += "### Removed Packages [%s]:\n\n" % len(removed_packages)
    for p in sorted(removed_packages):
        out += "- %s\n" % (conditional_markdown_package_homepage_link(p, old_packages),)
    out += "\n"

    out += \
        "Thanks to all ROS maintainers who make packages "\
        "available to the ROS community. The above list "\
        "of packages was made possible by the work of the "\
        "following maintainers: \n\n"
    for maintainer in sorted(maintainers):
        out += " * %s\n" % maintainer

    return out

import argparse
import re
import datetime
import os

from debian.debian_support import PackageFile


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


def main():
    """
    Usage: python diff_packages.py beforefile afterfile [--output-dir dir]
    Output: list of added/removed/versioned packages
    """
    usage = "usage: %prog fromfile tofile [rosdistro]"
    parser = argparse.ArgumentParser(usage)
    parser.add_argument('fromfile', type=str, nargs='+', default=None)
    parser.add_argument('tofile', type=str, nargs='+', default=None)
    parser.add_argument('rosdistro', type=str, default='groovy')
    parser.add_argument('--output-dir', dest='output_dir',
                        type=str, default='.')

    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        parser.error("Output directory [%s] does not exist aborting." %
                     args.output_dir)

    if not os.path.exists(args.fromfile[0]):
        parser.error("Missing input file from %s" % args.fromfile[0])

    if not os.path.exists(args.tofile[0]):
        parser.error("Missing input file from %s" % args.tofile[0])

    files = [args.fromfile[0], args.tofile[0]]
    fromlines = open(files[0], 'U')
    tolines = open(files[1], 'U')
    pf_old = PackageFile('old', fromlines)
    pf_new = PackageFile('new', tolines)

    old_packages = {}
    new_packages = {}

    for p in pf_old:
        intermediate = convert_tuples_list_to_dict(p)
        name = intermediate['Package']
        if args.rosdistro not in name:
            continue
        old_packages[name] = intermediate

    for p in pf_new:
        intermediate = convert_tuples_list_to_dict(p)
        name = intermediate['Package']
        if args.rosdistro not in name:
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

    dtime = datetime.datetime.now()
    dtime = dtime.replace(microsecond=0)
    filename = os.path.join(args.output_dir, '%s_%s.txt' %
                            (args.rosdistro, dtime.isoformat('-')))

    print("Writing to file %s" % filename)
    with open(filename, 'w') as fh:
        fh.write("Updates to %s\n\n" % args.rosdistro)
        fh.write("Added Packages [%s]:\n" % len(added_packages))
        for p in sorted(added_packages):
            fh.write(" * %s: %s\n" %
                     (p, core_version(new_packages[p]['Version'])))
        fh.write("\n\n")

        fh.write("Updated Packages [%s]:\n" % len(updated_packages))
        for p in sorted(updated_packages):
            fh.write(" * %s: %s -> %s\n" %
                     (p,
                      core_version(old_packages[p]['Version']),
                      core_version(new_packages[p]['Version'])))
        fh.write("\n\n")

        fh.write("Removed Packages [%s]:\n" % len(removed_packages))
        for p in sorted(removed_packages):
            fh.write("- %s\n" % (p))
        fh.write("\n\n")

        fh.write("Thanks to all ROS maintainers who make packages"
                 " available to the ROS community. The above list "
                 "of packages was made possible by the work of the"
                 " following maintainers:\n")
        for maintainer in sorted(maintainers):
            fh.write(" * %s\n" % maintainer)


if __name__ == '__main__':
    main()

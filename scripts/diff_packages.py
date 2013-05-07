import difflib
import argparse


def main():
    """
    Usage: python syncdiff.py beforefile afterfile
    Output: list of added/removed/versioned packages
    """
    usage = "usage: %prog fromfile tofile [rosdistro]"
    parser = argparse.ArgumentParser(usage)
    parser.add_argument('fromfile', type=str, nargs='+', default=None)
    parser.add_argument('tofile', type=str, nargs='+', default=None)
    parser.add_argument('rosdistro', type=str, default='groovy')

    args = parser.parse_args()

    files = [args.fromfile[0], args.tofile[0]]
    fromlines = open(files[0], 'U').readlines()
    tolines = open(files[1], 'U').readlines()
    diff = difflib.unified_diff(fromlines, tolines, files[0], files[1], n=5)
    diff = [l for l in diff if ('Version:' == l[1:9] or 'Package:' == l[1:9])]

    added_packages = {}
    removed_packages = {}
    versioned_packages = {}

    current_package = None
    current_package_mod = None
    current_version = None
    current_version_mod = None
    for line in diff:
        try:
            if 'Package:' == line[1:9]:
                current_package = line[line.index(':') + 2:-1]
                current_package_mod = line[0]
            elif 'Version:' == line[1:9]:
                current_version = version(line[line.index(':') + 2:-1])
                current_version_mod = line[0]
                if current_package_mod is ' ':
                    if current_package not in versioned_packages:
                        versioned_packages[current_package] = [None, None]
                    if current_version_mod == '-':
                        versioned_packages[current_package][0] = current_version
                    elif current_version_mod == '+':
                        versioned_packages[current_package][1] = current_version
                    else:
                        pass  # Diff static, Version not changed, ignore
                elif current_package_mod is '+':
                    if current_version_mod is not '+':
                        raise Exception(current_package + " add package odd ver")
                    if current_package in removed_packages:
                        temp = [current_version, removed_packages[current_package]]
                        del removed_packages[current_package]
                        versioned_packages[current_package] = temp
                        versioned_packages[current_package].sort()
                    else:
                        added_packages[current_package] = current_version
                elif current_package_mod is '-':
                    if current_version_mod is not '-':
                        raise Exception(current_package + " rem package odd ver")
                    if current_package in added_packages:
                        temp = [current_version, added_packages[current_package]]
                        del added_packages[current_package]
                        versioned_packages[current_package] = temp
                        versioned_packages[current_package].sort()
                    else:
                        removed_packages[current_package] = current_version
                else:
                    raise Exception("Erronious character: " + current_package_mod)
            else:
                raise Exception("Erronious line found: " + line)
        except Exception as ex:
            print "Excption parsing line:", ex

    print "\nPackages Added: "
    for line in sorted(added_packages):
        if args.rosdistro not in line:
            continue
        print line, ':', added_packages[line]
    print "\nPackages Removed: "
    for line in sorted(removed_packages):
        if args.rosdistro not in line:
            continue
        print line, ':', removed_packages[line]
    print "\nPackages Updated: "
    for line in sorted(versioned_packages):
        if args.rosdistro not in line:
            continue
        print_package = versioned_packages[line]
        if len(print_package) == 2 and print_package[0] != print_package[1]:
            print line, ':', print_package[0], '->', print_package[1]


def version(full_string):
    sectioned = full_string.split('-', 2)
    version_number = sectioned[0]
    if sectioned[1].isdigit():
        version_number = version_number + '-' + sectioned[1]
    return version_number

if __name__ == '__main__':
    main()

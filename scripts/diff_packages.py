import argparse
import datetime


from reprepro_updater import diff_repos


def main():
    """Output: list of added/removed/versioned packages."""
    usage = "usage: %prog fromfile tofile [rosdistro]"
    parser = argparse.ArgumentParser(usage)
    parser.add_argument('targetrepo', type=str, help='Destination repository base url')
    parser.add_argument('sourcerepo', type=str, help='Source repository base url')
    parser.add_argument('rosdistro', type=str, default='groovy')

    parser.add_argument('--component', type=str, default='main')
    parser.add_argument('--dist', type=str, default='trusty')
    parser.add_argument('--arch', type=str, default='binary-amd64')

    args = parser.parse_args()

    target_url = diff_repos.construct_packages_url(
        args.targetrepo,
        args.dist,
        args.component,
        args.arch
    )
    upstream_url = diff_repos.construct_packages_url(
        args.sourcerepo,
        args.dist,
        args.component,
        args.arch
    )

    try:
        pf_old = diff_repos.get_packagefile_from_url(target_url)
    except RuntimeError as ex:
        parser.error("%s" % ex)

    try:
        pf_new = diff_repos.get_packagefile_from_url(upstream_url)
    except RuntimeError as ex:
        parser.error("%s" % ex)

    dtime = datetime.datetime.now()
    dtime = dtime.replace(microsecond=0)

    print("Difference between '%s' and '%s' computed at %s" %
          (target_url, upstream_url, dtime.isoformat('-')))
    announcement = diff_repos.compute_annoucement(args.rosdistro, pf_old, pf_new)
    print(announcement)


if __name__ == '__main__':
    main()

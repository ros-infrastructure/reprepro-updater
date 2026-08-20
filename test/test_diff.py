import os

from reprepro_updater import diff_repos


def test_announcement():
    try:
        target_url = 'file://' + os.path.abspath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'test_data/Packages.target'))
        pf_old = diff_repos.get_packagefile_from_url(target_url)
    except RuntimeError:
        assert False

    try:
        upstream_url = 'file://' + os.path.abspath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'test_data/Packages.upstream'))
        pf_new = diff_repos.get_packagefile_from_url(upstream_url)
    except RuntimeError:
        assert False

    announcement = diff_repos.compute_annoucement('indigo', pf_old, pf_new)

    # Spot check results
    assert 'Removed Packages [10]:' in announcement
    assert 'Updated Packages [1740]:' in announcement
    assert 'Added Packages [214]:' in announcement


def get_test_packagefile(name):
    url = 'file://' + os.path.abspath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'test_data', name))
    return diff_repos.get_packagefile_from_url(url)


def test_strip_email():
    # bloom quotes the maintainer name since 0.14.3, but packages released
    # with an older bloom are still around, so both forms must be handled
    assert 'Bugs Bunny' == diff_repos.strip_email(
        'Bugs Bunny <bugs.bunny@openrobotics.org>')
    assert 'Bugs Bunny' == diff_repos.strip_email(
        '"Bugs Bunny" <bugs.bunny@openrobotics.org>')
    # names are not restricted to ASCII
    assert u'Pepé Le Pew' == diff_repos.strip_email(
        u'"Pepé Le Pew" <pepe.le.pew@openrobotics.org>')
    # a name may contain a comma, quoted or not
    assert 'Daffy Duck, Porky Pig' == diff_repos.strip_email(
        '"Daffy Duck, Porky Pig" <daffy.duck@acme.com>')
    assert 'Acme, Inc.' == diff_repos.strip_email(
        'Acme, Inc. <opensource@acme.com>')
    # a parenthesized comment is part of the name, it is not an address
    assert 'Wile E. Coyote (Super Genius)' == diff_repos.strip_email(
        'Wile E. Coyote (Super Genius) <wile.e.coyote@acme.com>')
    # the address is optional
    assert 'Acme Robotics' == diff_repos.strip_email('Acme Robotics')
    assert 'Acme Robotics' == diff_repos.strip_email('"Acme Robotics"')
    # a lone double quote is not a quoted name
    assert '"' == diff_repos.strip_email('"')
    # a name and an address that each hold several comma-separated values are
    # still a single entry, they are not split apart
    assert 'Yosemite Sam, Foghorn Leghorn' == diff_repos.strip_email(
        'Yosemite Sam, Foghorn Leghorn '
        '<yosemite.sam@openrobotics.org, foghorn.leghorn@acme.com>')
    assert 'Yosemite Sam, Foghorn Leghorn' == diff_repos.strip_email(
        '"Yosemite Sam, Foghorn Leghorn" '
        '<yosemite.sam@openrobotics.org, foghorn.leghorn@acme.com>')
    # a field holding several mailboxes also starts and ends with a quote, but
    # those quotes do not wrap a single name, so it is left untouched
    assert '"Tweety Bird" <tweety@openrobotics.org>, "Sylvester Cat"' == \
        diff_repos.strip_email(
            '"Tweety Bird" <tweety@openrobotics.org>, '
            '"Sylvester Cat" <sylvester@acme.com>')


def test_announcement_maintainer_names():
    pf_old = get_test_packagefile('Packages.maintainers.target')
    pf_new = get_test_packagefile('Packages.maintainers.upstream')

    announcement = diff_repos.compute_annoucement('humble', pf_old, pf_new)
    maintainers = announcement.split('following maintainers: \n\n')[1]

    # maintainer names are reported without the quotes bloom adds to them
    assert '"' not in maintainers
    assert ' * Bugs Bunny\n' in maintainers
    assert u' * Pepé Le Pew\n' in maintainers
    assert ' * Daffy Duck, Porky Pig\n' in maintainers
    assert ' * Acme, Inc.\n' in maintainers
    # a maintainer who released one package with a bloom that quotes the name
    # and another with a bloom that does not is only listed once
    assert 1 == maintainers.count(' * Bugs Bunny\n')
    assert 4 == len(maintainers.strip().splitlines())

    # the maintainer of a removed package is not credited
    assert 'Elmer Fudd' not in maintainers

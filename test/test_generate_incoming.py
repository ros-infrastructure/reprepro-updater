from reprepro_updater import conf


def test_imcoming():
    inc = conf.IncomingFile(['lucid', 'oneiric', 'precise'])
    contents = inc.generate_file_contents()
    assert """Name: lucid
IncomingDir: queue/lucid
TempDir: tmp
Allow: lucid

Name: oneiric
IncomingDir: queue/oneiric
TempDir: tmp
Allow: oneiric

Name: precise
IncomingDir: queue/precise
TempDir: tmp
Allow: precise

Name: all
IncomingDir: queue/all
TempDir: tmp
Allow: lucid oneiric precise
Cleanup: on_deny on_error
Options: multiple_distributions
""" in contents


def test_update_and_distributions():
    updates = conf.UpdatesFile(['lucid', 'oneiric', 'precise'], ['amd64', 'i386', 'armel'])


    dist = conf.DistributionsFile(['lucid', 'oneiric', 'precise'], ['amd64', 'i386', 'armel'], 'REPOKEYID', updates )
    dist_content = dist.generate_file_contents('amd64')
    assert """Origin: ROS
Label: ROS lucid
Codename: lucid
Suite: lucid
Architectures: amd64 i386 armel
Components: main
Description: ROS lucid Debian Repository
""" in dist_content

    assert "SignWith: REPOKEYID" in dist_content

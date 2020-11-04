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

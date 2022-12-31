"""
Args Tests.
"""
from flow.args import cli
from pytest import raises


def test_args():
    assert cli is not None
    # should exit when required params are not found
    with raises(SystemExit, match=r"2"):
        cli("profile")

    cmd = cli("profile", "dem.tif", "release.tif")
    assert cmd is not None
    assert cmd.command == "profile"

    # should exit when required params are not found
    with raises(SystemExit, match=r"2"):
        cli("release", "dem.tif", "release.tif")

    cmd = cli("release", "--alpha=25", "--exp=8", "dem.tif", "release.tif")
    assert cmd is not None
    assert cmd.command == "release"
    assert cmd.alpha_angle == 25
    assert cmd.exponent == 8

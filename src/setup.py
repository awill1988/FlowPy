"""The setup script."""
# setuptools must be imported first
from setuptools import setup, Distribution
from setuptools.command.install import install
import sys

# Workaround for the system-installed setuptools on macOS. That version wants
# to write bytecode files to locations that violate the sandbox, with this
# message:
#
#   The package setup script has attempted to modify files on your system
#   that are not within the EasyInstall build area, and has been aborted.
#
#   This package cannot be safely installed by EasyInstall, and may not
#   support alternate installation locations even if you run its setup
#   script by hand.  Please inform the package's author and the EasyInstall
#   maintainers to find out if a fix or workaround is available.
#
sys.dont_write_bytecode = True

if sys.version_info < (3, 10):
    print("project requires at least Python 3.10", file=sys.stderr)
    sys.exit(1)

from pathlib import Path  # noqa

# Change this to what you want your library code to be called!
PACKAGE_NAME = "flowpy"

# Path to the directory containing this file
PYTHON_ROOT = Path(__file__).parent.absolute()

# Relative path to this directory from cwd.
FROM_TOP = PYTHON_ROOT.relative_to(Path.cwd())

# Path to the root of the git checkout
SRC_ROOT = PYTHON_ROOT.parents[1]

# Not automatically updated!
version = "0.0.1"


def parse_requirements(fname="requirements.txt", with_version=True):
    """Parse the package dependencies listed in a requirements file but strip
    specific version information.
    Args:
        fname (str): Path to requirements file.
        with_version (bool, default=False): If True, include version specs.
    Returns:
        info (list[str]): List of requirements items.
    CommandLine:
        python -c "import setup; print(setup.parse_requirements())"
    """
    import re
    import sys
    from os.path import exists

    require_fpath = fname

    def parse_line(line):
        """Parse information from a line in a requirements text file."""
        if line.startswith("-r "):
            # Allow specifying requirements in other files
            target = line.split(" ")[1]
            for info in parse_require_file(target):
                yield info
        else:
            info = {"line": line}
            if line.startswith("-e "):
                info["package"] = line.split("#egg=")[1]
            else:
                # Remove versioning from the package
                pat = "(" + "|".join([">=", "==", ">"]) + ")"
                parts = re.split(pat, line, maxsplit=1)
                parts = [p.strip() for p in parts]

                info["package"] = parts[0]
                if len(parts) > 1:
                    op, rest = parts[1:]
                    if ";" in rest:
                        # Handle platform specific dependencies
                        # http://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-platform-specific-dependencies
                        version, platform_deps = map(str.strip, rest.split(";"))
                        info["platform_deps"] = platform_deps
                    else:
                        version = rest  # NOQA
                    info["version"] = (op, version)
            yield info

    def parse_require_file(fpath):
        with open(fpath, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    for info in parse_line(line):
                        yield info

    def gen_packages_items():
        if exists(require_fpath):
            for info in parse_require_file(require_fpath):
                parts = [info["package"]]
                if with_version and "version" in info:
                    parts.extend(info["version"])
                if not sys.version.startswith("3.4"):
                    # apparently package_deps are broken in 3.4
                    platform_deps = info.get("platform_deps")
                    if platform_deps is not None:
                        parts.append(";" + platform_deps)
                item = "".join(parts)
                yield item

    packages = list(gen_packages_items())
    return packages


class BinaryDistribution(Distribution):
    def is_pure(self):
        return False

    def has_ext_modules(self):
        return True


class InstallPlatlib(install):
    def finalize_options(self):
        install.finalize_options(self)
        if self.distribution.has_ext_modules():
            self.install_lib = self.install_platlib


setup(
    name=PACKAGE_NAME,
    version=version,
    description="Flow-Py Library SDK",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: >=3.10",
    ],
    install_requires=parse_requirements("requirements/runtime.txt"),
    keywords=f"{PACKAGE_NAME}",
    package_dir={
        PACKAGE_NAME: FROM_TOP / "flowpy",
    },
    package_data={PACKAGE_NAME: [str(FROM_TOP / "py.typed")]},
    include_package_data=True,
    distclass=BinaryDistribution,
    cmdclass={"install": InstallPlatlib},
    scripts=["bin/flowpy"],
    zip_safe=True,
)

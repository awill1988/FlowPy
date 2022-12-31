# file system utilities
from tempfile import mkdtemp
from typing import Optional
from zipfile import ZipFile
from tarfile import open as open_tarfile


def unarchive(location: str, output_dir: Optional[str] = None) -> None:
    """Unarchives a compressed set of data onto the filesystem."""
    output_dir = output_dir or mkdtemp()
    assert location.endswith(".tar.gz") or location.endswith(".zip")
    if location.endswith(".zip"):
        with ZipFile(location) as zipfile:
            ZipFile.extractall(zipfile, path=output_dir)
    else:
        with open_tarfile(location, "r:gz") as tarfile:
            tarfile.extractall(output_dir)

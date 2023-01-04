
#**************************************************************************************************
#                                      Build Arguments
#--------------------------------------------------------------------------------------------------
#   Query a version (or to check if one is available), run on terminal:
#
#   `docker run -it osgeo/gdal bash -c 'apt update && apt-cache madison build-essential'`
#
#   The Qt5 dependency list was generated with:
#
#   `docker run -it osgeo/gdal bash -c 'apt update && apt list "libqt5*-dev" "qt*5-dev"'`
#
#--------------------------------------------------------------------------------------------------

# GDAL Version
#--------------------------------------------------------------------------------------------------
ARG GDAL_VERSION="3.6.2"

# APT Version Pins
#--------------------------------------------------------------------------------------------------
ARG APT_BUILD_ESSENTIAL_VERSION="12.9ubuntu3"
ARG APT_CA_CERTIFICATES_VERSION="20211016ubuntu0.22.04.1"
ARG APT_PYTHON3_DEV_VERSION="3.10.6-1~22.04"
ARG APT_PYTHON3_PIP_VERSION="22.0.2+dfsg-1"
ARG APT_PYTHON3_PYQT5_VERSION="5.15.6+dfsg-1ubuntu3"

# Python Enviornment Dependencies
#--------------------------------------------------------------------------------------------------
ARG PYTHON3_NUMPY_VERSION="1.24.1"
ARG PYTHON3_CYTHON_VERSION="0.29.33"
ARG PYTHON3_PIP_VERSION="22.3.1"

#**************************************************************************************************
#                                    the development environment
#--------------------------------------------------------------------------------------------------
FROM osgeo/gdal:ubuntu-full-${GDAL_VERSION} as build-base

ARG APT_BUILD_ESSENTIAL_VERSION \
    APT_CA_CERTIFICATES_VERSION \
    APT_PYTHON3_DEV_VERSION \
    APT_PYTHON3_PIP_VERSION \
    APT_PYTHON3_PYQT5_VERSION \
    PYTHON3_NUMPY_VERSION \
    PYTHON3_CYTHON_VERSION \
    PYTHON3_PIP_VERSION

# Set an initial working directory of "/usr/src"
#--------------------------------------------------------------------------------------------------
WORKDIR /usr/src

# Copy installation requirements
#--------------------------------------------------------------------------------------------------
COPY requirements.txt requirements.txt

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN \
    #----------------------------------------------------------------------------------------------
    # update system package manager
    #----------------------------------------------------------------------------------------------
    apt-get update && \
    #----------------------------------------------------------------------------------------------
    # install system dependencies
    #----------------------------------------------------------------------------------------------
    apt-get install -y --no-install-recommends \
    "build-essential=${APT_BUILD_ESSENTIAL_VERSION}" \
    "ca-certificates=${APT_CA_CERTIFICATES_VERSION}" \
    "python3-pip=${APT_PYTHON3_PIP_VERSION}" \
    "python3-pyqt5=${APT_PYTHON3_PYQT5_VERSION}" \
    "python3-dev=${APT_PYTHON3_DEV_VERSION}" && \
    #----------------------------------------------------------------------------------------------
    # upgrade pip
    #----------------------------------------------------------------------------------------------
    pip install -U "pip==${PYTHON3_PIP_VERSION}" && \
    #----------------------------------------------------------------------------------------------
    # numpy install dependency for next line
    #----------------------------------------------------------------------------------------------
    python -m pip install --user "numpy==${PYTHON3_NUMPY_VERSION}" && \
    #----------------------------------------------------------------------------------------------
    # dependency for packaging rasterio into bdist
    #----------------------------------------------------------------------------------------------
    python -m pip install --user "Cython==${PYTHON3_CYTHON_VERSION}" --install-option="--no-cython-compile" && \
    #----------------------------------------------------------------------------------------------
    # this helps do a bit of caching in the container in this step
    #----------------------------------------------------------------------------------------------
    python -m pip install --user -r requirements.txt && \
    #----------------------------------------------------------------------------------------------
    # clean apt cache
    #----------------------------------------------------------------------------------------------
    apt-get clean && \
    #----------------------------------------------------------------------------------------------
    # clean apt lists
    #----------------------------------------------------------------------------------------------
    rm -rf /var/lib/apt/lists/*

#**************************************************************************************************
#                                    the development environment
#--------------------------------------------------------------------------------------------------
FROM build-base as shell

COPY . .

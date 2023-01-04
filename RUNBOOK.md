# Runbook

useful commands you may need to run:

## Python Virtual Environment

First thing to setup is to make sure you have Python 3.10:

```bash
python --version
```

should look like `Python 3.10.7`

Next, run `make`

## Docker Image with GDAL 3.6.1

```bash
docker build -t flowpy:develop --target=develop .
docker run -it flowpy:develop gdal-config --version
```

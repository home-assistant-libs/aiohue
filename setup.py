"""Setup for aiohue."""
from setuptools import find_packages, setup

LONG_DESC = open("README.md").read()
PACKAGES = find_packages(exclude=["tests", "tests.*"])
REQUIREMENTS = list(val.strip() for val in open("requirements.txt"))
MIN_PY_VERSION = "3.8"

setup(
    name="aiohue",
    version="3.0.7",
    license="Apache License 2.0",
    url="https://github.com/home-assistant-libs/aiohue",
    author="Paulus Schoutsen",
    author_email="paulus@paulusschoutsen.nl",
    description="Python module to talk to Philips Hue.",
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",
    packages=PACKAGES,
    zip_safe=True,
    platforms="any",
    install_requires=REQUIREMENTS,
    python_requires=f">={MIN_PY_VERSION}",
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

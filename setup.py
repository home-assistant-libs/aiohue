"""Setup for aiohue."""
from setuptools import find_packages, setup

LONG_DESC = open("README.md").read()
PACKAGES = find_packages(exclude=["tests", "tests.*"])

setup(
    name="aiohue",
    version="2.6.5",
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
    install_requires=list(val.strip() for val in open("requirements.txt")),
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

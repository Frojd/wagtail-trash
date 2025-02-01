#!/usr/bin/env python
from setuptools import find_packages, setup

with open("wagtail_trash/version.py", "r") as f:
    version = None
    exec(f.read())

with open("README.md", "r") as f:
    readme = f.read()

testing_extras = ["black", "wagtail-factories"]

setup(
    name="wagtail-trash",
    version=version,
    description="Make deleted pages only temporarily deleted.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Andreas Bernacca",
    author_email="ante.bernacca@gmail.com",
    install_requires=[
        "wagtail>=5.2",
        "wagtail-modeladmin",
    ],
    extras_require={
        "testing": testing_extras,
    },
    setup_requires=["wheel"],
    zip_safe=False,
    license="MIT License",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    package_data={},
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 5",
        "Framework :: Wagtail :: 6",
        "License :: OSI Approved :: MIT License",
    ],
    project_urls={
        "Source": "https://github.com/Frojd/wagtail-trash/",
        "Changelog": "https://github.com/Frojd/wagtail-trash/blob/main/CHANGELOG.md",
    },
)

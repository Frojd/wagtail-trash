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
        "wagtail>=2.14,<2.16",
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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 2",
        "License :: OSI Approved :: MIT License",
    ],
    project_urls={
        "Source": "https://github.com/Frojd/wagtail-trash/",
        "Changelog": "https://github.com/Frojd/wagtail-trash/blob/main/CHANGELOG.md",
    },
)

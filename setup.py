from pathlib import Path

from setuptools import find_packages, setup

version = None
exec(Path("wagtail_trash/version.py").read_text(encoding="utf-8"))  # noqa: S102

readme = Path("README.md").read_text(encoding="utf-8")

testing_extras = ["wagtail-factories>=4.5"]

setup(
    name="wagtail-trash",
    version=version,
    description="Make deleted pages only temporarily deleted.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Andreas Bernacca",
    author_email="ante.bernacca@gmail.com",
    install_requires=[
        "wagtail>=7.4",
        "wagtail-modeladmin>=2.5",
    ],
    python_requires=">=3.11",
    extras_require={
        "testing": testing_extras,
    },
    zip_safe=False,
    license_expression="MIT",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    package_data={},
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Framework :: Django",
        "Framework :: Django :: 5.2",
        "Framework :: Django :: 6.0",
        "Framework :: Django :: 6.1",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 7",
        "Framework :: Wagtail :: 8",
    ],
    project_urls={
        "Source": "https://github.com/Frojd/wagtail-trash/",
        "Changelog": "https://github.com/Frojd/wagtail-trash/blob/main/CHANGELOG.md",
    },
)

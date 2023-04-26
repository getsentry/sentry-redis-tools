from setuptools import find_packages, setup

from typing import Sequence


setup(
    name="sentry-redis-tools",
    version="0.1.5",
    author="Sentry",
    author_email="oss@sentry.io",
    url="https://github.com/getsentry/sentry-redis-tools",
    description="Common utilities related to how Sentry uses Redis",
    zip_safe=False,
    install_requires=['redis>=3.0'],
    packages=find_packages(exclude=("tests", "tests.*")),
    package_data={"sentry_redis_tools": ["py.typed"]},
    include_package_data=True,
    options={"bdist_wheel": {"universal": "1"}},
)

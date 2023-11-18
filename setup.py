from setuptools import setup

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="dj-admin-plus",
    version="0.0.1",
    description="DJ Admin plus is a pluggable easy to use modern admin for Django framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    package_dir={'dj_admin_plus': 'dj_admin_plus'},
    package_data={
        'dj_admin_plus': [
            '**/*.html',
            '**/*.css',
            '**/*.js',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

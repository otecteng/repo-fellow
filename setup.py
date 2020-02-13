import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "repofellow",
    version = "0.0.1",
    author = "tli",
    author_email = "otec.teng@gmail.com",
    description = "repo metric collector",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/otecteng/repo-fellow",
    packages = setuptools.find_packages(),
    include_package_data = True,
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "SQLAlchemy==1.3.13",
        "requests==2.22.0",
        "requests-html==0.9.0",
        "docopt==0.6.2",
        "docutils==0.14",
        "mysql-connector==2.2.9",
        "PyMySQL==0.9.3"
    ],
    entry_points={
        "console_scripts": ["repofellow = repofellow.__main__:main"] 
    }

)
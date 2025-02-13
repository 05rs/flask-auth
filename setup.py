from setuptools import setup, find_packages

# Define package metadata
NAME = "flask-oauth-guard"
VERSION = "0.0.87"
AUTHOR = "Raghav Sethi"
AUTHOR_EMAIL = "work.raghavsethi@gmail.com"
DESCRIPTION = "A Flask extension to add Authentication and Authorization, supports OAuth2"
URL = "https://github.com/05rs/flask-auth"
LICENSE = "Apache"

# Define dependencies (if any)
INSTALL_REQUIRES = [
    "Flask",
    "authlib",
    "requests",
    "urllib3==1.26.15",
    "flask-sqlalchemy",
    "flask-wtf",
    "psycopg2-binary",
    "PyJWT",
    "python-dotenv==1.0.1"
]



# Find package structure
PACKAGES = ["flask_auth_wrapper", "flask_auth_wrapper.models", "flask_auth_wrapper.services"]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


# Create setup arguments
setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    url=URL,
    license=LICENSE,
    install_requires=INSTALL_REQUIRES,
    packages=PACKAGES,
    long_description=long_description,
    long_description_content_type="text/markdown",
)

# python3 setup.py sdist bdist_wheel

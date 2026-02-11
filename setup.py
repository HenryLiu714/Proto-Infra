"""Setup configuration for Trading Infrastructure."""

from setuptools import setup, find_packages

setup(
    name="trading-infra",
    version="0.1.0",
    description="Trading infrastructure with database operations",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        "console_scripts": [
            "trading-engine=src.main:main",
        ],
    },
)

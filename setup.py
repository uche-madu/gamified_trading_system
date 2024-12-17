from setuptools import setup, find_packages

setup(
    name="gamified_trading_system",
    version="0.1.0",
    packages=find_packages(where="app"),  # Specify 'app' as the package directory
    package_dir={"": "app"},             # Map root packages to the 'app' folder
    install_requires=[
        # Add your dependencies here
        "fastapi",
        "uvicorn",
        "pydantic",
        "pytest",
    ],
)

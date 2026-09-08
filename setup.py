from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="forgemind",
    version="0.1.0",
    description="MCP-native multi-agent AI platform with approvals, traces, and evals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kamalesh",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={"src.dashboard": ["*.html", "*.js", "*.css"]},
    install_requires=[
        "click>=8.0",
        "fastapi>=0.100",
        "uvicorn>=0.20",
    ],
    extras_require={
        "local": ["llama-cpp-python>=0.2"],
        "dev": ["pytest>=7.0", "httpx", "ruff", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "forgemind=src.cli.main:cli",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)

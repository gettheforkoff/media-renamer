from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="media-renamer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to rename movie and TV show files using metadata from TVDB and TMDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/media-renamer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
        "click>=8.0.0",
        "guessit>=3.4.0",
        "pymediainfo>=6.0.0",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "media-renamer=src.cli:main",
        ],
    },
)
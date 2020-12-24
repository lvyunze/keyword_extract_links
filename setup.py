from setuptools import setup
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='keyword_extract_links',
    version='0.0.4',
    packages=['keyword_extract_links'],
    author="lvyunze",
    author_email="17817462542@163.com",
    description="This is a package that extracts keyword links based on web keywords",
    keywords="extracts keyword links based on web keywords",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lvyunze/keyword_extract_links",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['lxml==4.6.2'],
)

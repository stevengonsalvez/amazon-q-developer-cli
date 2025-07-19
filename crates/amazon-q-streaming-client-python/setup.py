from setuptools import setup, find_packages

setup(
    name='amazon-q-streaming-client',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'httpx',
        'pydantic',
    ],
    author='Amazon Q Developer CLI',
    description='A Python client for the Amazon Q streaming API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/aws-samples/amazon-q-developer-cli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)

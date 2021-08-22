import os
import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='scrooge-mcduck',
    version='0.0.1+%s' % os.environ['CI_APPLICATION_TAG'],
    author='Anton Chernev',
    author_email='anton.chernev@seequestor.com',
    description='Duck tales!',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://example.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    python_requires='>=3.6',
    install_requires=[
        'celery>=5.1.2',
        'psycopg2-binary>=2.9.1',
        'requests>=2.26.0',
        'SQLAlchemy>=1.4.23',
    ],
)

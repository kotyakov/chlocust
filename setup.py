from setuptools import (
    find_packages,
    setup
)


setup(
    name='chlocust',
    version='0.1.4',
    packages=find_packages(exclude=('*.tests', '*.tests.*', 'tests.*', 'tests')),
    install_requires=(
        'locustio>=0.11.0',
        'clickhouse-driver>=0.1.1'
    ),

    author='Maxim Kotyakov',
    author_email='m.a.kotyakov@yandex.ru',
    description='Locust plugin for ClickHouse load testing',
    url='https://github.com/kotyakov/chlocust',

    zip_safe=True,

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

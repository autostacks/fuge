# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='openstack-fuge',
    version='1.0',
    author='Cyan',
    author_email='autostack@163.com',
    description='Container as a service for OpenStack.',
    license='OpenStack',
    include_package_data=True,
    data_files=[('/etc/fuge', ['etc/api-paste.ini', 'etc/fuge.conf', 'etc/policy.json']),
                ('/etc/logrotate.d', ['etc/openstack-fuge']),
                ('/usr/lib/systemd/system', ['usr/openstack-fuge-api.service',
                                             'usr/openstack-fuge-conductor.service'])
                ],
    classifier=[
        'Environment :: OpenStack',
        'Intended Audience :: Information Technology',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7']
)

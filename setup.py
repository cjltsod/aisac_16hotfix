from setuptools import setup

setup(
    name='aisac_16hotfix',
    version='0.0',
    description='2016 Hotfix for aisac proxy',
    url='https://github.com/cjltsod/aisac_16hotfix',
    author='CJLTSOD',
    author_email='aisac_16hotfix.github.tsod@tsod.idv.tw',
    packages=['aisac_16hotfix'],
    install_requires=[
        'cython',
        'sqlalchemy',
        'suds-py3',
        'mysqlclient',
        'paramiko',
        'psutil',
        # 'pyjnius',
    ],
    dependency_links=[
        # 'git+https://github.com/kivy/pyjnius.git#egg=pyjnius',
    ],
    zip_safe=False,
)

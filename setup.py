from setuptools import setup, find_packages
import os

import cartodbsync


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
]

setup(
    author='Eric Brelsford',
    author_email='ebrelsford@gmail.com',
    name='django-cartodb-sync',
    version=cartodbsync.__version__,
    description=("A Django app that helps keep CartoDB tables synchronized with Django models."),
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='https://github.com/ebrelsford/django-cartodb-sync',
    license='BSD License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django>=1.8',
        'cartodb>=0.8',
    ],
    packages=find_packages(),
    include_package_data=True,
)

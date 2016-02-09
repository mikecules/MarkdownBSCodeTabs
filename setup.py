#!/usr/bin/env python

from setuptools import setup

setup(
    name='BSCodeTabs',
    version='1.0',
    py_modules=['BSCodeTabExtension'],
    install_requires = ['markdown>=2.6'],
    description='Converts Fenced Sequential Blocks in Markdown into Bootstrap HTML Tabs.',
    author='Michael Moncada',
    author_email='michael.moncada@gmail.com',
    license='GPL3',
    platforms='Operating System :: OS Independent',
    long_description="""This plugin will convert consecutive fences blocks and convert it to HTML Bootstrap Tabs.
    PLEASE NOTE: this extension requires Bootstrap 3.x+ to work correctly the frontend/browser."""
)

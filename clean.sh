#!/bin/sh

rm distribute-*.tar.gz
rm *.egg
find -name '*.pyc' -delete
rm -rf dist
rm -rf build
rm -rf deb_dist
rm -rf src/*.egg-info

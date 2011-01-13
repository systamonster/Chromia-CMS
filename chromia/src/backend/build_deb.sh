#!/bin/sh
#
# Copyright (C) 2011 Kirill Gordeev <kirill.gordeev@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

OUT_BUILD_DIR="/home/kg/builds/pub/"
IN_SOURCE_DIR="$2"
BUILD_DIR="/home/kg/builds/$1/"

MAINTANER_EMAIL="kirill.gordeev@gmail.com"

mkdir $BUILD_DIR
cp -rf $IN_SOURCE_DIR* $BUILD_DIR
cd $BUILD_DIR; ./autogen.sh
echo "ok" | dh_make --createorig -s -e $MAINTANER_EMAIL -c gpl2
dpkg-buildpackage -rfakeroot
cd ..; cp -rf *i386.deb $OUT_BUILD_DIR
rm -rf $BUILD_DIR
rm -rf *diff.gz *.dsc *.changes *.deb *.tar.gz
echo "Done"

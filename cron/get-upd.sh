#!/bin/bash

apt-get -s -o Debug::NoLocking=true upgrade | grep -c ^Inst

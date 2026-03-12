#!/bin/sh -x
CURRENT=`git name-rev HEAD --name-only`
git checkout trial
git pull origin trial
git checkout trial
git rebase trial



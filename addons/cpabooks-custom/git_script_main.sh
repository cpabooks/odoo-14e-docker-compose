#!/bin/sh -x
CURRENT=`git name-rev HEAD --name-only`
git checkout main
git pull origin main
git checkout ${CURRENT}
git rebase main



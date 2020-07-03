#!/bin/bash
docker build --tag=tasker:sha-$(git rev-parse --short=7 HEAD) .

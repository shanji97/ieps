#!/bin/bash

PGPASSWORD="5loFzWry6ZwC" pg_dump -h ep-falling-block-598917.eu-central-1.aws.neon.tech -Fc -U orglce neondb > pa1/database/crawldb-$(date +"%Y_%m_%d_%I_%M").dump


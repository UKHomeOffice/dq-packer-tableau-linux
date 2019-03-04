#!/bin/bash

tsm data-access repository-access enable --repository-username "$TAB_INT_TABSVR_REPO_USER" --repository-password "$TAB_INT_TABSVR_REPO_PASSWORD" --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"

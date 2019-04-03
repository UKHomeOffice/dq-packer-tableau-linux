#!/bin/bash

tsm licenses activate --license-key "$TAB_PRODUCT_KEY_1" --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
tsm licenses activate --license-key "$TAB_PRODUCT_KEY_2" --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
tsm licenses activate --license-key "$TAB_PRODUCT_KEY_3" --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
tsm licenses activate --license-key "$TAB_PRODUCT_KEY_4" --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
tsm restart --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"

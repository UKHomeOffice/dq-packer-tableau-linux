#!/bin/bash

tsm licenses deactivate --license-key "$TAB_PRODUCT_KEY_1" -u "$TAB_SRV_USER" -p "$TAB_SRV_PASSWORD"
tsm licenses deactivate --license-key "$TAB_PRODUCT_KEY_2" -u "$TAB_SRV_USER" -p "$TAB_SRV_PASSWORD"
tsm licenses deactivate --license-key "$TAB_PRODUCT_KEY_3" -u "$TAB_SRV_USER" -p "$TAB_SRV_PASSWORD"

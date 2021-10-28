#!/bin/bash

# There's a bug with the initial admin password generation.
# See here: https://www.browserling.com/tools/bcrypt
# bcrypt(thisisdumb)=$2a$10$bZ6QaPQbGrYVU2o0.YUWx.otMasaq3g2VVkrgHn.5sgKFBMKRAQ0i
kubectl -n "$1" patch secret argocd-secret \
  -p '{"stringData": {
    "admin.password": "$2a$10$bZ6QaPQbGrYVU2o0.YUWx.otMasaq3g2VVkrgHn.5sgKFBMKRAQ0i",
    "admin.passwordMtime": "'$(date +%FT%T%Z)'"
  }}'

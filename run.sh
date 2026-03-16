#!/usr/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

./.venv/bin/uvicorn app.main:app \
  --host 127.0.0.1 \
  --port 8000 \
  --ssl-keyfile key.pem \
  --ssl-certfile cert.pem \
  --reload
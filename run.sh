#!/usr/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

echo "Competition backend - Copyright (C) 2026 Otto Crawford "
echo "This program comes with ABSOLUTELY NO WARRANTY; " \
      "This is free software, and you are welcome to redistribute it" \
      "under certain conditions;" \

./.venv/bin/uvicorn app:app \
  --host 127.0.0.1 \
  --port 8000 \
  --ssl-keyfile key.pem \
  --ssl-certfile cert.pem \
  --reload
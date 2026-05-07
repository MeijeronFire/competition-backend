# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

Write-Output "Competition backend - Copyright (C) 2026 Otto Crawford "
Write-Output "This program comes with ABSOLUTELY NO WARRANTY; " \
      "This is free software, and you are welcome to redistribute it" \
      "under certain conditions;" \

python -m uvicorn app:app `
  --host 0.0.0.0 `
  --port 8000 `
  --ssl-keyfile key.pem `
  --ssl-certfile cert.pem `
  --reload
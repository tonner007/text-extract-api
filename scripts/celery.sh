#!/bin/bash
echo "DANE"
echo "$@"
cd "$(dirname "$0")/.." || exit 1
echo "EXEC"
exec celery -A text_extract_api.tasks "$@"

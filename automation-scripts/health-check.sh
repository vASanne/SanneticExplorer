#!/bin/bash
# Sannetic Explorer - health-check.sh
echo "🚀 Running health-check.sh..."
cd /app && make status
echo "✅ health-check.sh completed"

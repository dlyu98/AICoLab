#!/usr/bin/env bash
curl -X POST http://localhost:8000/v1/agent/respond \
  -H "Content-Type: application/json" \
  -d @examples/sample_request.json

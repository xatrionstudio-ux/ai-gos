# Getting Started with AGOS

> **Stripe/OpenAI-Style Quickstart Guide for Developers & Growth Engineers.**

---

## 1. Installation

### Python SDK
```bash
pip install agos-sdk
```

### TypeScript SDK
```bash
pnpm add @agos/sdk
```

---

## 2. Quickstart Example (Python)

```python
from agos_sdk import AGOSClient

# Initialize client
client = AGOSClient(api_key="agos_live_90128490128490")

# 1. Inspect System Health
print(client.health())

# 2. List SaaS Projects
projects = client.list_projects()
print(f"Active Projects: {len(projects)}")
```

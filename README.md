# envdiff

> Compare `.env` files across environments and surface missing or mismatched keys.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/envdiff.git
cd envdiff
pip install .
```

---

## Usage

```bash
envdiff .env.development .env.production
```

**Example output:**

```
Missing in .env.production:
  - DATABASE_URL
  - REDIS_HOST

Mismatched keys:
  - LOG_LEVEL: "debug" vs "info"
  - PORT: "3000" vs "8080"
```

You can also compare more than two files at once:

```bash
envdiff .env.development .env.staging .env.production
```

### Python API

```python
from envdiff import compare

results = compare(".env.development", ".env.production")
print(results.missing)
print(results.mismatched)
```

---

## Options

| Flag | Description |
|------|-------------|
| `--keys-only` | Only check for missing keys, ignore value differences |
| `--quiet` | Suppress output, exit with non-zero code on diff |
| `--json` | Output results as JSON |

---

## License

This project is licensed under the [MIT License](LICENSE).
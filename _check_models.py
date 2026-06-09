import urllib.request, json
try:
    data = json.loads(urllib.request.urlopen("http://localhost:11434/api/tags", timeout=10).read())
    models = data.get("models", [])
    if not models:
        print("No models found")
    else:
        for m in models:
            name = m.get("name", "?")
            size = float(m.get("size", 0)) / 1e9
            print(f"  - {name:<40s} {size:.2f} GB")
except Exception as e:
    print(f"ERROR: {e}")

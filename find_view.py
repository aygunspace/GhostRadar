import json

with open("overview_copy.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    try:
        obj = json.loads(line)
        if obj.get("type") == "VIEW_FILE" and "index.html" in obj.get("content", ""):
            print(f"Step: {obj.get('step_index')}")
            content = obj.get("content")
            if "Showing lines 1 to 89" in content or "Total Lines: 89" in content:
                print("Found large view! Lines snippet:")
                # print first 100 chars
                print(content[:100])
    except:
        pass

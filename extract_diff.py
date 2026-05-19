import json
import re

with open("overview_copy.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    try:
        obj = json.loads(line)
        if obj.get("type") == "CODE_ACTION" and "index.html" in obj.get("content", "") and "The following changes were made by the USER" in obj.get("content", ""):
            content = obj.get("content")
            # Write it out to parse
            with open("user_diffs.txt", "a", encoding="utf-8") as out:
                out.write(content + "\n\n====\n\n")
    except:
        pass

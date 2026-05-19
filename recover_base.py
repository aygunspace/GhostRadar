import os
import re

log_path = r"C:\Users\EXCALIBUR\.gemini\antigravity\brain\c0c8addb-0e45-450c-9e03-71ca2f301179\.system_generated\logs\overview.txt"

with open(log_path, 'r', encoding='utf-8') as f:
    content = f.read()

# find "1: <!DOCTYPE html>" and "894: " or similar at the end
start_idx = content.find("1: <!DOCTYPE html>\n2: <html lang=\"tr\">")
if start_idx != -1:
    end_idx = content.find("894:     </script>", start_idx)
    if end_idx != -1:
        end_idx = content.find("</html>", end_idx) + 7
        
        block = content[start_idx:end_idx]
        lines = block.split('\n')
        
        clean_lines = []
        for line in lines:
            clean_line = re.sub(r"^\d+:\s", "", line)
            clean_lines.append(clean_line)
            
        with open("recovered_index_base.html", "w", encoding="utf-8") as out:
            out.write('\n'.join(clean_lines))
        print("Recovered base! Lines:", len(clean_lines))
    else:
        print("Found start but not 894:")
else:
    print("Could not find start 1: <!DOCTYPE html>")

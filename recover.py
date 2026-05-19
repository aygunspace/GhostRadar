import os

log_path = r"C:\Users\EXCALIBUR\.gemini\antigravity\brain\c0c8addb-0e45-450c-9e03-71ca2f301179\.system_generated\logs\overview.txt"

with open(log_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all occurrences of "1: <!DOCTYPE html>"
start_idx = 0
found_blocks = []
while True:
    idx = content.find("1: <!DOCTYPE html>", start_idx)
    if idx == -1:
        break
    
    # find the end of this block, which is usually indicated by "The above content does NOT show" or something similar
    end_idx = content.find("The above content does NOT show the entire file contents.", idx)
    if end_idx == -1:
        end_idx = content.find("The following code has been modified", idx)
        if end_idx == -1:
            end_idx = idx + 60000 # Just take a huge chunk and we'll trim it
            
    block = content[idx:end_idx]
    if len(block.split('\n')) > 500: # We know the file is ~899 lines
        found_blocks.append(block)
    
    start_idx = idx + 1

if found_blocks:
    # Get the last valid block
    last_block = found_blocks[-1]
    
    lines = last_block.split('\n')
    clean_lines = []
    for line in lines:
        if line.startswith('The above') or line.startswith('The following') or line.strip() == '':
            continue
            
        import re
        clean_line = re.sub(r"^\d+:\s", "", line)
        clean_lines.append(clean_line)
        
        # Stop if we hit </html>
        if clean_line.strip() == '</html>':
            break

    with open("recovered_index.html", "w", encoding="utf-8") as out:
        out.write('\n'.join(clean_lines))
    print("Recovered! Lines:", len(clean_lines))
else:
    print("Could not find any block with >500 lines.")

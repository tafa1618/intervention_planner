
with open("backend_full.log", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "Found PSSR_Client" in line:
            print(f"Match at line {i+1}: {line.strip()}")
            for j in range(1, 21):
                if i + j < len(lines):
                    print(f"Line {i+1+j}: {lines[i+j].strip()}")

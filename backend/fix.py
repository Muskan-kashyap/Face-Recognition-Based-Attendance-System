with open("app/db/models/__init__.py") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "──" in line and not line.lstrip().startswith("#"):
        new_lines.append("# " + line)
    elif "=====" in line and not line.lstrip().startswith("#"):
        new_lines.append("# " + line)
    else:
        new_lines.append(line)

with open("app/db/models/__init__.py", "w") as f:
    f.writelines(new_lines)

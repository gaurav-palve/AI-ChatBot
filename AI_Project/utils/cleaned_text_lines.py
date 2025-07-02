def clean_text(lines):
    cleaned_lines = []
    for line in lines:
        # Strip leading/trailing spaces and reduce multiple spaces to one
        cleaned_line = ' '.join(line.strip().split())
        cleaned_lines.append(cleaned_line)
    return cleaned_lines
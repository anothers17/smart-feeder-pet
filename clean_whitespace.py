
import os
import glob

def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = [line.rstrip() + '\n' for line in lines]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    print(f"Cleaned {filepath}")

for filepath in glob.glob('**/*.py', recursive=True):
    if 'venv' not in filepath:
        clean_file(filepath)

import os
import re
import shutil

def convert_zim_to_markdown(zim_text):
    # Converting headers
    zim_text = re.sub(r'======\s?(.*?)\s?======', r'# \1', zim_text)
    zim_text = re.sub(r'=====\s?(.*?)\s?=====', r'## \1', zim_text)
    zim_text = re.sub(r'====\s?(.*?)\s?====', r'### \1', zim_text)
    zim_text = re.sub(r'===\s?(.*?)\s?===', r'#### \1', zim_text)
    zim_text = re.sub(r'==\s?(.*?)\s?==', r'##### \1', zim_text)

    # Converting links
    zim_text = re.sub(r'\[\[(.*?)\|?(.*?)\]\]', lambda m: f"[{m.group(2) or m.group(1)}]({m.group(1).replace(' ', '-')})", zim_text)

    # Handling tables
    lines = zim_text.split('\n')
    converted_lines = []
    in_table = False

    for line in lines:
        if '|' in line and not line.strip().startswith('//'):  # assuming '//' starts a comment line
            if not in_table:
                converted_lines.append('|' + line.strip().replace(':|', '|').replace('|', ' | ') + '|')
                column_count = line.count('|') - 1
                converted_lines.append('|' + ' --- |' * column_count)
                in_table = True
            else:
                converted_lines.append('|' + line.strip().replace(':|', '|').replace('|', ' | ') + '|')
        else:
            in_table = False
            converted_lines.append(line)

    return '\n'.join(converted_lines)

def process_directory(source, destination):
    # Ensure destination directory exists
    if not os.path.exists(destination):
        os.makedirs(destination)

    # Copy all directories and files from source to destination
    for item in os.listdir(source):
        s_item = os.path.join(source, item)
        d_item = os.path.join(destination, item)

        if os.path.isdir(s_item):
            process_directory(s_item, d_item)  # Recursive call for directories
        elif s_item.endswith('.txt'):  # Assuming ZIM files are .txt files
            with open(s_item, 'r', encoding='utf-8') as file:
                content = file.read()
            markdown_content = convert_zim_to_markdown(content)
            d_item = os.path.splitext(d_item)[0] + '.md'  # Change extension to .md for Markdown
            with open(d_item, 'w', encoding='utf-8') as file:
                file.write(markdown_content)
        else:
            shutil.copy2(s_item, d_item)  # Copy other files directly

def main():
    source_dir = input("Enter the source directory (ZIM wiki location): ")
    destination_dir = input("Enter the destination directory (Obsidian vault location): ")

    process_directory(source_dir, destination_dir)
    print("Migration completed successfully!")

if __name__ == "__main__":
    main()

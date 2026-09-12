import os
import re

base_dir = os.path.dirname(os.path.abspath(__file__))
temporaries_dir = os.path.join(base_dir, 'temporaries')
logs_html_path = os.path.join(base_dir, 'logs.html')

def get_md_files(dir_path):
    md_files = []
    if not os.path.exists(dir_path):
        return md_files
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return md_files

def parse_front_matter(content):
    match = re.search(r'^---\r?\n([\s\S]*?)\r?\n---', content)
    metadata = {}
    if match:
        lines = match.group(1).split('\n')
        for line in lines:
            if ':' in line:
                key, val = line.split(':', 1)
                metadata[key.strip()] = val.strip().strip('"\'')
    return metadata

def parse_body(content):
    body = re.sub(r'^---\r?\n[\s\S]*?\r?\n---', '', content).strip()
    body = re.sub(r'^### Q\. (.*$)', r'<p><strong>Q. \1</strong></p>', body, flags=re.M)
    body = re.sub(r'^### A\. (.*$)', r'<hr><p><strong>A. \1</strong></p>', body, flags=re.M)
    body = re.sub(r'^\- (.*$)', r'<li>\1</li>', body, flags=re.M)
    body = re.sub(r'`(.*?)`', r'<code>\1</code>', body)
    body = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', body)
    return body

def build():
    md_files = get_md_files(temporaries_dir)
    if not md_files:
        print("対象の .md ファイルが見つかりませんでした。")
        return

    cards_html = ""
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        meta = parse_front_matter(content)
        body_html = parse_body(content)

        date = meta.get('date', '日付不明')
        category = meta.get('category', '未分類')
        title = meta.get('title', os.path.basename(file_path))

        cards_html += f"""
<!-- Auto Generated Card: {os.path.basename(file_path)} -->
<article class="log-card">
  <div class="log-date">{date} | {category}</div>
  <h2 class="log-title">{title}</h2>
  <div class="log-body">
    {body_html}
  </div>
</article>
"""

    if not os.path.exists(logs_html_path):
        print("logs.html が見つかりません。")
        return

    with open(logs_html_path, 'r', encoding='utf-8') as f:
        logs_content = f.read()

    start_marker = '<!-- AUTO-BUILD-START -->'
    end_marker = '<!-- AUTO-BUILD-END -->'

    if start_marker in logs_content and end_marker in logs_content:
        pattern = f"{re.escape(start_marker)}[\\s\\S]*?{re.escape(end_marker)}"
        new_content = re.sub(pattern, f"{start_marker}\n{cards_html}\n{end_marker}", logs_content)
        with open(logs_html_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Pythonで logs.html にカードを自動反映しました！")
    else:
        print("⚠️ AUTO-BUILD マーカーが見つかりません。")

if __name__ == '__main__':
    build()
    
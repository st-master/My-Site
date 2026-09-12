const fs = require('fs');
const path = require('path');

const temporariesDir = path.join(__dirname, 'temporaries');
const logsHtmlPath = path.join(__dirname, 'logs.html');

// 再帰的に .md ファイルを取得する関数
function getMdFiles(dir, fileList = []) {
  if (!fs.existsSync(dir)) return fileList;
  const files = fs.readdirSync(dir);
  files.forEach(file => {
    const filePath = path.join(dir, file);
    if (fs.statSync(filePath).isDirectory()) {
      getMdFiles(filePath, fileList);
    } else if (file.endsWith('.md')) {
      fileList.push(filePath);
    }
  });
  return fileList;
}

// 簡易 Front Matter (YAMLヘッダー) 解析
function parseFrontMatter(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  const metadata = {};
  if (match) {
    const lines = match[1].split('\n');
    lines.forEach(line => {
      const [key, ...valueParts] = line.split(':');
      if (key && valueParts.length > 0) {
        metadata[key.trim()] = valueParts.join(':').trim().replace(/^['"]|['"]$/g, '');
      }
    });
  }
  return metadata;
}

// 本文からQ&A部を抽出・変換
function parseBodyToCards(content) {
  const body = content.replace(/^---\r?\n[\s\S]*?\r?\n---/, '').trim();
  // リスト項目などをHTML化
  const htmlBody = body
    .replace(/^### Q\. (.*$)/gim, '<p><strong>Q. $1</strong></p>')
    .replace(/^### A\. (.*$)/gim, '<hr><p><strong>A. $1</strong></p>')
    .replace(/^\- (.*$)/gim, '<li>$1</li>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  return htmlBody;
}

function build() {
  const mdFiles = getMdFiles(temporariesDir);
  if (mdFiles.length === 0) {
    console.log('対象となる .md ファイルが見つかりませんでした。');
    return;
  }

  let generatedCardsHtml = '';

  mdFiles.forEach(filePath => {
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    const meta = parseFrontMatter(fileContent);
    const bodyHtml = parseBodyToCards(fileContent);

    const date = meta.date || '日付不明';
    const category = meta.category || '未分類';
    const title = meta.title || path.basename(filePath, '.md');
    generatedCardsHtml += `
    <!-- Auto Generated Card: ${path.basename(filePath)} -->
    <article class="log-card">
    <div class="log-date">${date} | ${category}</div>
    <h2 class="log-title">${title}</h2>
    <div class="log-body">
        ${bodyHtml}
    </div>
    </article>
`;
  });

  // logs.html の読み込みと更新
  if (!fs.existsSync(logsHtmlPath)) {
    console.error('logs.html が見つかりません。');
    return;
  }

  let logsContent = fs.readFileSync(logsHtmlPath, 'utf-8');

  // 挿入用のマーカー（コメントタグ）
  const startMarker = '<!-- AUTO-BUILD-START -->';
  const endMarker = '<!-- AUTO-BUILD-END -->';

  if (logsContent.includes(startMarker) && logsContent.includes(endMarker)) {
    const regex = new RegExp(`${startMarker}[\\s\\S]*?${endMarker}`);
    logsContent = logsContent.replace(regex, `${startMarker}\n${generatedCardsHtml}\n${endMarker}`);
    fs.writeFileSync(logsHtmlPath, logsContent, 'utf-8');
    console.log('✅ logs.html にカードを自動反映しました！');
  } else {
    console.log(`⚠️ logs.html 内に ${startMarker} と ${endMarker} のマーカータグを追加してください。`);
  }
}

build();
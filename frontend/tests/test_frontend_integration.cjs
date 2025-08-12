#!/usr/bin/env node
/**
 * フロントエンド統合テスト
 * 
 * フロントエンドのビルド、型チェック、リント、
 * およびAPI連携の基本的な動作確認を行います。
 */

const { exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs').promises;
const path = require('path');

const execAsync = promisify(exec);

// テスト結果を格納
const testResults = {
  実行日時: new Date().toISOString(),
  環境: 'development',
  テスト項目: []
};

// 色付きコンソール出力
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

async function runTest(name, command, cwd = '.') {
  log(`\n🧪 ${name}...`, 'blue');
  const startTime = Date.now();
  
  try {
    const { stdout, stderr } = await execAsync(command, { cwd });
    const duration = Date.now() - startTime;
    
    log(`✅ ${name}: 成功 (${duration}ms)`, 'green');
    
    testResults.テスト項目.push({
      項目: name,
      結果: '成功',
      実行時間: `${duration}ms`,
      詳細: stdout ? stdout.substring(0, 200) : ''
    });
    
    return { success: true, stdout, stderr };
  } catch (error) {
    const duration = Date.now() - startTime;
    
    log(`❌ ${name}: 失敗 (${duration}ms)`, 'red');
    if (error.stderr) {
      log(`  エラー: ${error.stderr.substring(0, 200)}`, 'yellow');
    }
    
    testResults.テスト項目.push({
      項目: name,
      結果: '失敗',
      実行時間: `${duration}ms`,
      エラー: error.message || error.stderr
    });
    
    return { success: false, error };
  }
}

async function checkFileExists(filePath, description) {
  try {
    await fs.access(filePath);
    log(`✅ ${description}: 存在確認OK`, 'green');
    testResults.テスト項目.push({
      項目: description,
      結果: '成功',
      詳細: filePath
    });
    return true;
  } catch {
    log(`❌ ${description}: ファイルが見つかりません`, 'red');
    testResults.テスト項目.push({
      項目: description,
      結果: '失敗',
      詳細: `${filePath} が存在しません`
    });
    return false;
  }
}

async function main() {
  log('=' * 60, 'blue');
  log('フロントエンド統合テスト', 'blue');
  log('=' * 60, 'blue');
  
  // 1. 環境確認
  log('\n【1. 環境確認】', 'blue');
  await runTest('Node.jsバージョン確認', 'node --version');
  await runTest('npmバージョン確認', 'npm --version');
  
  // 2. 依存関係チェック
  log('\n【2. 依存関係チェック】', 'blue');
  await runTest('package.json検証', 'npm ls --depth=0 --json > /dev/null 2>&1 && echo "OK"');
  
  // 3. 重要ファイルの存在確認
  log('\n【3. 重要ファイルの存在確認】', 'blue');
  await checkFileExists('package.json', 'package.json');
  await checkFileExists('tsconfig.json', 'TypeScript設定');
  await checkFileExists('vite.config.ts', 'Vite設定');
  await checkFileExists('tailwind.config.js', 'Tailwind設定');
  await checkFileExists('src/main.tsx', 'エントリーポイント');
  await checkFileExists('src/App.tsx', 'Appコンポーネント');
  
  // 4. TypeScriptコンパイルチェック
  log('\n【4. TypeScriptコンパイルチェック】', 'blue');
  await runTest('型チェック', 'npx tsc --noEmit');
  
  // 5. ESLintチェック
  log('\n【5. ESLintチェック】', 'blue');
  const lintResult = await runTest('Lintチェック', 'npm run lint 2>&1 | head -20');
  
  // 6. ビルドテスト
  log('\n【6. ビルドテスト】', 'blue');
  const buildResult = await runTest('プロダクションビルド', 'npm run build');
  
  if (buildResult.success) {
    // ビルド成果物の確認
    await checkFileExists('dist/index.html', 'ビルド成果物(HTML)');
    await checkFileExists('dist/assets', 'ビルド成果物(Assets)');
  }
  
  // 7. APIエンドポイント定義の確認
  log('\n【7. API連携確認】', 'blue');
  await checkFileExists('src/core/api/chat.ts', 'Chat API定義');
  await checkFileExists('src/core/api/agent.ts', 'Agent API定義');
  await checkFileExists('src/core/api/webcrawl.ts', 'WebCrawl API定義');
  await checkFileExists('src/core/api/taskTemplates.ts', 'TaskTemplates API定義');
  
  // 8. コンポーネント構造の確認
  log('\n【8. コンポーネント構造確認】', 'blue');
  await checkFileExists('src/features/chat/pages/Chat.tsx', 'Chatページ');
  await checkFileExists('src/pages/Library/index.tsx', 'Libraryページ');
  await checkFileExists('src/shared/components/Layout/index.tsx', 'Layoutコンポーネント');
  
  // テスト結果のサマリー
  log('\n' + '=' * 60, 'blue');
  log('テスト結果サマリー', 'blue');
  log('=' * 60, 'blue');
  
  const successCount = testResults.テスト項目.filter(item => item.結果 === '成功').length;
  const totalCount = testResults.テスト項目.length;
  const successRate = Math.round((successCount / totalCount) * 100);
  
  log(`\n成功: ${successCount}/${totalCount} (${successRate}%)`, successRate === 100 ? 'green' : 'yellow');
  
  // 失敗した項目を表示
  const failures = testResults.テスト項目.filter(item => item.結果 === '失敗');
  if (failures.length > 0) {
    log('\n失敗した項目:', 'red');
    failures.forEach(item => {
      log(`  ❌ ${item.項目}`, 'red');
      if (item.エラー) {
        log(`     ${item.エラー.substring(0, 100)}`, 'yellow');
      }
    });
  }
  
  // 結果をJSONファイルに保存
  const resultsPath = path.join(__dirname, 'test_frontend_results.json');
  await fs.writeFile(resultsPath, JSON.stringify(testResults, null, 2));
  log(`\nテスト結果を ${resultsPath} に保存しました`, 'green');
  
  process.exit(failures.length > 0 ? 1 : 0);
}

// テスト実行
main().catch(error => {
  log(`\n予期しないエラー: ${error.message}`, 'red');
  process.exit(1);
});
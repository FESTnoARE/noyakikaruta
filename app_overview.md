# のやきかるたアプリ開発計画

## システム概要
ユーザーが登録した文字列をランダムに表示するWebアプリケーション

## 技術スタック
- フレームワーク：Streamlit
- バックエンド：Python 3.8+
- データベース：PostgreSQL (via Streamlit Connection)
- デプロイ：Streamlit Cloud
- ホスティング：GitHub

## 実装済み機能

### 基本機能
- 文字列の登録・表示
  - 管理者による文字列登録
  - 登録済み文字列の一覧表示
  - ランダム表示機能
  - 前後ナビゲーション機能

### 管理者機能
- パスワード認証による管理者ログイン
- 文字列の登録・削除権限管理
- CSV一括登録機能
  - UTF-8, Shift-JIS, CP932対応
  - プレビュー機能
  - サンプルCSVダウンロード

### UI/UX
- レスポンシブデザイン
- スマートフォン最適化
- カラーコーディングによる視認性向上
- 直感的な操作性

## デプロイ手順

### 1. 事前準備
- GitHubリポジトリの作成
- 必要なファイルの準備
  ```
  app.py              # メインアプリケーション
  requirements.txt    # 依存パッケージ
  config.example.py   # 設定ファイルテンプレート
  .gitignore         # Git除外設定
  ```

### 2. Streamlit Cloud設定
1. https://share.streamlit.io/ でデプロイ
2. GitHubリポジトリと連携
3. シークレット設定
   - アプリケーション管理画面の「Settings」>「Secrets」に以下の内容を貼り付けます。
   - `your_secure_password` は任意の管理者パスワードに置き換えてください。
   - `[connections.postgresql]` の下には、ご自身で用意したPostgreSQLデータベースの接続情報を記述します。

   ```toml
   # .streamlit/secrets.toml

   # 管理者パスワード
   ADMIN_PASSWORD = "your_secure_password"

   # PostgreSQLデータベース接続情報
   [connections.postgresql]
   dialect = "postgresql"
   host = "your_db_host"
   port = 5432
   database = "your_db_name"
   username = "your_db_user"
   password = "your_db_password"
   ```

### プロジェクトディレクトリ構成
```
noyakikaruta/
├── app.py              # メインアプリケーション
├── database.py         # データベース操作モジュール
├── requirements.txt    # 依存パッケージ
├── .gitignore         # Git除外設定
└── .streamlit/
    └── secrets.toml    # (Streamlit Cloud上で管理)
```

### セキュリティ対策
1. 設定管理
   - 機密情報（DB接続情報、管理者パスワード）はStreamlit Cloudのシークレットで管理
   - 設定ファイルのテンプレート化

2. アクセス制御
   - 管理者機能のパスワード保護
   - 文字列登録・削除の権限管理

3. データ保護
   - データベースへの直接アクセスを制限
   - 機密情報をコードから分離

### 今後の改善点
1. 機能追加
   - 文字列の編集機能
   - タグ付け機能
   - 検索機能

2. UI/UX改善
   - アニメーション効果の追加
   - テーマカスタマイズ
   - 表示レイアウトの多様化

3. 運用管理
   - バックアップ機能
   - 利用統計の収集
   - エラーログの管理


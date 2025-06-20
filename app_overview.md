# のやきかるたアプリ開発計画

## システム概要
ユーザーが登録した文字列をランダムに表示するWebアプリケーション

## 技術スタック
- フレームワーク：Streamlit
- バックエンド：Python 3.8+
- データベース：Turso (via st-turso)
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
3. **Tursoデータベースの準備**
   1. [Turso](https://turso.tech/)にサインアップし、新しいデータベースを作成します。
   2. データベースの管理画面で、**データベースURL**（`libsql://...`という形式）と**認証トークン**を取得します。
4. **シークレット設定**
   - Streamlit Cloudのアプリケーション管理画面で「Settings」>「Secrets」に以下の内容を貼り付けます。
   - `your_secure_password` は任意の管理者パスワードに置き換えてください。
   - `url` と `authToken` には、上で取得したTursoの情報を設定します。

   ```toml
   # .streamlit/secrets.toml

   # 管理者パスワード
   ADMIN_PASSWORD = "your_secure_password"

   # Tursoデータベース接続情報
   [connections.turso]
   url = "libsql://your-database-name.turso.io"
   authToken = "your-long-auth-token"
   ```

### プロジェクトディレクトリ構成
```

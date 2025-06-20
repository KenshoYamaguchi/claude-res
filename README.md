# コワーキングスペース予約システム

Flaskを使用したWebベースのコワーキングスペース予約システムです。

## 機能

- 会員登録・ログイン機能
- 管理者による会員承認機能
- カレンダー表示による予約状況確認
- 予約の作成・管理
- メール通知機能
- 管理者画面

## システム要件

- Python 3.7以上
- Flask
- SQLite3

## インストールと設定

### 1. 必要なパッケージのインストール

```bash
pip install flask
```

### 2. 設定ファイルの編集

`config.json`ファイルを編集して、メール設定を行ってください：

```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your_email@gmail.com",
  "smtp_password": "your_app_password",
  "admin_email": "admin@example.com",
  "email_notifications": true
}
```

### 3. データベースの初期化

アプリケーションを最初に起動すると、自動的にSQLiteデータベースが作成されます。

### 4. 管理者アカウント

初回起動時に以下の管理者アカウントが作成されます：

- **メールアドレス**: admin@example.com
- **パスワード**: admin123

**重要**: 初回ログイン後、必ずパスワードを変更してください。

## 起動方法

### 開発環境での起動

```bash
python app.py
```

### Windowsサーバーでの起動

```bash
run_server.bat
```

アプリケーションは `http://localhost:5000` でアクセスできます。

## 使用方法

### 一般ユーザー

1. トップページから「会員登録」をクリック
2. 必要事項を入力して登録申請
3. 管理者による承認を待つ
4. 承認後、ログインして予約を作成

### 管理者

1. 管理者アカウントでログイン
2. 「管理者」メニューから承認待ちユーザーを確認
3. 「承認」ボタンをクリックしてユーザーを承認

## 予約ルール

- **営業時間**: 平日 9:00 - 18:00
- **最低予約時間**: 1時間
- **最大予約時間**: 1日8時間
- **予約可能期間**: 30日先まで
- **休業日**: 日曜日

## ファイル構成

```
/
├── app.py              # Flaskアプリケーション本体
├── config.json         # 設定ファイル
├── utils.py           # ユーティリティ関数
├── coworking.db       # SQLiteデータベース（自動生成）
├── templates/         # HTMLテンプレート
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── admin.html
├── static/           # 静的ファイル
│   ├── style.css
│   └── calendar.js
├── README.md
└── run_server.bat    # Windows起動スクリプト
```

## データベース構造

### users テーブル
- id: ユーザーID
- name: ユーザー名
- email: メールアドレス
- password_hash: パスワードハッシュ
- is_approved: 承認状態
- is_admin: 管理者フラグ
- created_at: 作成日時

### reservations テーブル
- id: 予約ID
- user_id: ユーザーID
- date: 予約日
- start_time: 開始時間
- end_time: 終了時間
- purpose: 利用目的
- created_at: 作成日時

## トラブルシューティング

### メール送信エラー

- Gmailを使用する場合は、アプリパスワードを使用してください
- 2段階認証を有効にしてアプリパスワードを生成してください

### データベースエラー

- `coworking.db`ファイルを削除して再起動すると、データベースが再作成されます
- 重要なデータがある場合は、事前にバックアップを取ってください

### ポートエラー

- ポート5000が使用中の場合は、`app.py`の最後の行を変更してください：
  ```python
  app.run(debug=True, host='0.0.0.0', port=8000)
  ```

## セキュリティ注意事項

- 本番環境では`app.secret_key`を変更してください
- HTTPSを使用することを推奨します
- 定期的にパスワードを更新してください
- データベースのバックアップを定期的に取ってください

## ライセンス

このプロジェクトはオープンソースです。

## サポート

問題が発生した場合は、システム管理者にお問い合わせください。
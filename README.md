# WalkorBuss

愛知工業大学から八草駅までの通勤経路（徒歩 or バス）を判断するWebアプリケーションです。
次のバスの時刻、電車の接続情報、現在の天気を総合的に判断し、最適な移動手段を提案します。

## 前提条件

### 必要なソフトウェア

- **Python 3.8 以上**（動作確認済み: Python 3.13）
- **pip**（Pythonパッケージマネージャー）

### 必要なAPIキー

- **OpenWeatherMap API Key**
  - 天気情報の取得に使用します
  - [OpenWeatherMap](https://openweathermap.org/api) で無料アカウントを作成し、APIキーを取得してください

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <リポジトリURL>
cd WalkorBuss
```

### 2. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

インストールされるライブラリ:
- Flask（Webフレームワーク）
- python-dotenv（環境変数管理）
- requests（HTTP通信）

### 3. 環境変数の設定

`.env.example` をコピーして `.env` ファイルを作成します。

```bash
cp .env.example .env
```

作成した `.env` ファイルを開き、APIキーを設定してください。

```bash
WEATHER_API_KEY=your_api_key_here  # ← ここを実際のAPIキーに置き換える
```

**APIキーの取得方法:**
1. [OpenWeatherMap](https://openweathermap.org/) にアクセス
2. アカウントを作成（無料）
3. ログイン後、右上の自身のユーザーネームをクリックし、メニューからMy API keys をクリックします。「API keys」タブからAPIキーをコピー
4. `.env` ファイルの `your_api_key_here` を取得したAPIキーに置き換え

## 実行方法

### アプリケーションの起動

```bash
python app.py
```

### ブラウザでアクセス

アプリケーション起動後、以下のURLにアクセスしてください。



```
http://localhost:5000
```

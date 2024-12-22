# Pythonイメージを使用
FROM python:3.9-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコピー
COPY . .

# サーバーを起動
CMD ["python", "main.py"]
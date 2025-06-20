# 設定ファイルのテンプレート
# 1. このファイルを config.py としてコピー
# 2. パスワードを変更
# 3. config.py は .gitignore に含まれているため、リポジトリにはコミットされません

# このファイルを config.py にコピーして使用してください
# ローカル開発用のパスワード設定
import streamlit as st
ADMIN_PASSWORD = "your_password_here"

# Streamlit Cloud用のシークレット管理

# Streamlit Cloudでは.streamlit/secrets.tomlの値を使用
if 'ADMIN_PASSWORD' in st.secrets:
    ADMIN_PASSWORD = st.secrets['ADMIN_PASSWORD']

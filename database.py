import streamlit as st
import pandas as pd
import sqlalchemy
from sqlalchemy import text

# sqlalchemy-libsqlをインポートすることで、SQLAlchemyに 'libsql' dialectを登録します。
# これにより、create_engineが 'libsql://' で始まるURLを解釈できるようになります。
import sqlalchemy_libsql

# StreamlitのConnection機能を利用してデータベース接続を管理
# @st.cache_resourceデコレータで接続オブジェクトをキャッシュし、パフォーマンスを向上


@st.cache_resource
def get_connection():
    """データベース接続用のSQLAlchemy Engineを取得する"""
    try:
        url = st.secrets["connections"]["turso"]["url"]
        token = st.secrets["connections"]["turso"]["token"]
    except KeyError:
        st.error("Tursoの接続情報（url, token）が .streamlit/secrets.toml に正しく設定されていません。")
        st.stop()

    # sqlalchemy-libsql用の接続URLを構築します
    # フォーマット: libsql://<hostname>/?authToken=<token>
    full_url = f"{url}?authToken={token}"

    return sqlalchemy.create_engine(full_url)

# データベースのテーブルを初期化


def init_db():
    """データベースを初期化する"""
    engine = get_connection()
    with engine.begin() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS strings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        '''))

# 単一の文字列をデータベースに追加


def add_string(string_content: str):
    """文字列を登録する"""
    engine = get_connection()
    with engine.begin() as conn:
        conn.execute(
            text('INSERT INTO strings (content) VALUES (:content)'),
            {"content": string_content}
        )

# 複数の文字列をリストから一括で追加


def add_multiple_strings(string_list: list[str]):
    """複数の文字列を一括登録する"""
    engine = get_connection()
    df = pd.DataFrame(string_list, columns=["content"])
    df.to_sql('strings', engine, if_exists='append', index=False)

# 登録されているすべての文字列を取得


def get_all_strings():
    """すべての文字列を登録日時が新しい順に取得する"""
    engine = get_connection()
    with engine.connect() as conn:
        df = pd.read_sql(
            'SELECT * FROM strings ORDER BY created_at DESC;', conn)
    return df

# 登録されているすべての文字列をランダムな順序で取得


def get_all_strings_random():
    """すべての文字列をランダムな順序で取得する"""
    engine = get_connection()
    with engine.connect() as conn:
        df = pd.read_sql('SELECT * FROM strings ORDER BY RANDOM();', conn)
    return df

# 指定したIDの文字列を削除


def delete_string(string_id: int):
    """指定されたIDの文字列を削除する"""
    engine = get_connection()
    with engine.begin() as conn:
        conn.execute(
            text('DELETE FROM strings WHERE id = :id'),
            {"id": string_id}
        )

# すべての文字列を削除


def delete_all_strings():
    """すべての文字列を削除する"""
    engine = get_connection()
    with engine.begin() as conn:
        conn.execute(text('DELETE FROM strings;'))
        conn.execute(text('VACUUM;'))

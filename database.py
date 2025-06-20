import streamlit as st
import pandas as pd
import sqlalchemy_libsql

# StreamlitのConnection機能を利用してデータベース接続を管理
# @st.cache_resourceデコレータで接続オブジェクトをキャッシュし、パフォーマンスを向上


@st.cache_resource
def get_connection():
    """データベース接続を取得する"""
    # Streamlitの汎用SQL接続機能を使用し、Tursoデータベースに接続します。
    # 接続情報は .streamlit/secrets.toml から自動的に読み込まれます。
    return st.connection("turso", type="sql")

# データベースのテーブルを初期化


def init_db():
    """データベースを初期化する"""
    conn = get_connection()
    with conn.session as s:
        # "strings"テーブルが存在しない場合のみ作成
        # SQLiteでは `SERIAL PRIMARY KEY` の代わりに `INTEGER PRIMARY KEY AUTOINCREMENT` を使用
        # `TIMESTAMP WITH TIME ZONE` は `DATETIME` に変更
        s.execute('''
            CREATE TABLE IF NOT EXISTS strings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        s.commit()

# 単一の文字列をデータベースに追加


def add_string(string_content: str):
    """文字列を登録する"""
    conn = get_connection()
    with conn.session as s:
        # パラメータ化クエリでSQLインジェクションを防止
        s.execute('INSERT INTO strings (content) VALUES (?)',
                  (string_content,))
        s.commit()

# 複数の文字列をリストから一括で追加


def add_multiple_strings(string_list: list[str]):
    """複数の文字列を一括登録する"""
    conn = get_connection()
    # Pandas DataFrameに変換してからSQLに書き込むことで高速化
    df = pd.DataFrame(string_list, columns=["content"])
    # `to_sql`は内部で効率的な一括挿入を行う
    df.to_sql('strings', conn.engine, if_exists='append', index=False)

# 登録されているすべての文字列を取得


def get_all_strings():
    """すべての文字列を登録日時が新しい順に取得する"""
    conn = get_connection()
    # `conn.query`はクエリ結果をPandas DataFrameとして返す
    df = conn.query('SELECT * FROM strings ORDER BY created_at DESC;')
    return df

# 登録されているすべての文字列をランダムな順序で取得


def get_all_strings_random():
    """すべての文字列をランダムな順序で取得する"""
    conn = get_connection()
    # SQLiteのRANDOM()関数でランダムな並び替えを実現
    df = conn.query('SELECT * FROM strings ORDER BY RANDOM();')
    return df

# 指定したIDの文字列を削除


def delete_string(string_id: int):
    """指定されたIDの文字列を削除する"""
    conn = get_connection()
    with conn.session as s:
        s.execute('DELETE FROM strings WHERE id = ?', (string_id,))
        s.commit()

# すべての文字列を削除


def delete_all_strings():
    """すべての文字列を削除する"""
    conn = get_connection()
    with conn.session as s:
        # SQLiteではTRUNCATE TABLEの代わりにDELETE FROMを使用
        s.execute('DELETE FROM strings;')
        # VACUUMで空き領域を解放（任意）
        s.execute('VACUUM;')
        s.commit()

"""
のやき札アプリケーション

文字列をランダムに表示するStreamlitウェブアプリケーション
"""

# 標準ライブラリ
import hashlib
import io
import os
import random
import sqlite3

# サードパーティライブラリ
import pandas as pd
import streamlit as st

# 設定ファイルの読み込み
try:
    # Streamlit Cloudの場合
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except KeyError:
    try:
        # ローカル環境の場合
        from config import ADMIN_PASSWORD
    except ImportError:
        st.error("""
        設定ファイルが見つかりません。
        1. config.example.py を config.py にコピー
        2. config.py 内のパスワードを変更
        してください。
        """)
        st.stop()

# ページ設定
st.set_page_config(
    page_title="のやき札",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# セッション状態の初期化
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'random_strings' not in st.session_state:
    st.session_state.random_strings = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

# データベース接続関数


def get_db_connection():
    """データベース接続を取得する"""
    if not os.path.exists('data'):
        os.makedirs('data')
    conn = sqlite3.connect('data/karuta.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_card_colors(string_id):
    """文字列IDに基づいて背景色と文字色を生成する"""
    # 文字列IDをシードとして使用
    card_colors = [
        {"bg": "#E6F3FF", "text": "#003366"},  # 薄い青 - 濃い青
        {"bg": "#FFE6E6", "text": "#660000"},  # 薄い赤 - 濃い赤
        {"bg": "#E6FFE6", "text": "#006600"},  # 薄い緑 - 濃い緑
        {"bg": "#FFE6FF", "text": "#660066"},  # 薄い紫 - 濃い紫
        {"bg": "#FFF3E6", "text": "#663300"},  # 薄いオレンジ - 茶色
        {"bg": "#E6FFFF", "text": "#006666"},  # 薄い水色 - 濃い青緑
    ]
    return card_colors[string_id % len(card_colors)]

# パスワードをハッシュ化する関数


def hash_password(input_password):
    """パスワードをハッシュ化する"""
    return hashlib.sha256(input_password.encode()).hexdigest()

# 管理者認証


def authenticate_admin(input_password):
    """管理者認証を行う"""
    return hash_password(input_password) == hash_password(ADMIN_PASSWORD)


# CSSでスタイルを適用
st.markdown("""
<style>
    /* 全体のスタイル */
    .main {
        padding: 0.5rem;
    }
    
    /* サイドバーのスタイル */
    .css-1d391kg {
        padding: 1rem 0.5rem;
    }
    
    /* ボタンのスタイル */
    .stButton>button {
        width: 100%;
        margin: 0.5rem 0;
        padding: 0.5rem;
        font-size: 1.1rem;
    }
    
    /* カードのスタイル */
    .card {
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e6e6e6;
        margin: 0.5rem 0;
        position: relative;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 管理者フォームのスタイル */
    .admin-form {
        margin: 1rem 0;
        padding: 0.8rem;
        border: 1px solid #e6e6e6;
        border-radius: 8px;
    }
    
    /* コンテンツコンテナのスタイル */
    .content-container {
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* ナビゲーションテキストのスタイル */
    .navigation-text {
        font-size: 1.5rem;
        color: #0066cc;
        margin: 0.5rem 0;
    }
    
    /* テキストエリアのスタイル */
    .stTextArea textarea {
        font-size: 1.1rem;
        line-height: 1.5;
    }
    
    /* 文字列表示のスタイル */
    .card h2 {
        font-size: 1.3rem;
        line-height: 1.4;
        margin: 0;
        word-break: break-all;
    }
    
    /* 登録日時のスタイル */
    .card small {
        font-size: 0.8rem;
        color: #666;
        display: block;
        margin-top: 0.5rem;
    }
    
    /* スマートフォン向けの調整 */
    @media (max-width: 768px) {
        .main {
            padding: 0.3rem;
        }
        .card {
            padding: 0.8rem;
            margin: 0.3rem 0;
        }
        .stButton>button {
            padding: 0.8rem;
            font-size: 1rem;
        }
        .navigation-text {
            font-size: 1.2rem;
        }
        .card h2 {
            font-size: 1.1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# タイトルとヘッダー
st.title("のやき札")
st.markdown("---")

# サイドバーメニュー
with st.sidebar:
    st.header("メニュー")
    page = st.radio(
        "ページ選択",
        ["ランダム表示", "文字列登録", "一覧表示"]
    )

    # 管理者ログインフォーム
    if not st.session_state.is_admin:
        st.markdown("---")
        st.subheader("管理者ログイン")
        with st.form("login_form"):
            password = st.text_input("パスワード", type="password")
            if st.form_submit_button("ログイン"):
                if authenticate_admin(password):
                    st.session_state.is_admin = True
                    st.success("ログインしました！")
                    st.rerun()
                else:
                    st.error("パスワードが正しくありません。")
    else:
        st.markdown("---")
        if st.button("ログアウト"):
            st.session_state.is_admin = False
            st.rerun()

# データベース初期化


def init_db():
    """データベースを初期化する"""
    if not os.path.exists('data'):
        os.makedirs('data')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS strings
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         content TEXT NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

# 文字列の登録


def add_string(string_content):
    """文字列を登録する"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO strings (content) VALUES (?)', (string_content,))
    conn.commit()
    conn.close()

# 複数の文字列を一括登録


def add_multiple_strings(string_list):
    """複数の文字列を一括登録する"""
    conn = get_db_connection()
    c = conn.cursor()
    for string_content in string_list:
        if string_content and not string_content.isspace():  # 空文字列やスペースのみは除外
            c.execute('INSERT INTO strings (content) VALUES (?)',
                      (string_content,))
    conn.commit()
    conn.close()

# 全ての文字列を取得


def get_all_strings():
    """全ての文字列を取得する"""
    conn = get_db_connection()
    c = conn.cursor()
    result = c.execute(
        'SELECT * FROM strings ORDER BY created_at DESC').fetchall()
    conn.close()
    return result

# 全ての文字列をランダムな順序で取得


def get_all_strings_random():
    """全ての文字列をランダムな順序で取得する"""
    conn = get_db_connection()
    c = conn.cursor()
    result = c.execute('SELECT * FROM strings').fetchall()
    conn.close()
    # リストに変換してシャッフル
    result_list = [dict(s) for s in result]
    random.shuffle(result_list)
    return result_list

# 文字列の削除


def delete_string(string_id):
    """指定されたIDの文字列を削除する"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM strings WHERE id = ?', (string_id,))
    conn.commit()
    conn.close()

# 全ての文字列を削除


def delete_all_strings():
    """全ての文字列を削除する"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM strings')
    conn.commit()
    conn.close()


# データベースの初期化
init_db()

# ページ内容の表示
if page == "ランダム表示":
    st.header("ランダム表示")

    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        if st.button("ランダム表示", key="random_button"):
            # 新しいランダム配列を生成
            strings = get_all_strings_random()
            if strings:
                st.session_state.random_strings = strings
                st.session_state.current_index = 0
            else:
                st.warning("登録された文字列がありません。")
                st.session_state.random_strings = []
                st.session_state.current_index = 0

    # ナビゲーションと文字列表示
    if st.session_state.random_strings:
        current_string = st.session_state.random_strings[st.session_state.current_index]

        # ナビゲーションボタンと文字列表示
        col1, col2, col3 = st.columns([1, 4, 1])

        with col1:
            if st.button("＜", key="prev", disabled=st.session_state.current_index == 0):
                st.session_state.current_index -= 1
                st.rerun()

        with col2:
            colors = get_card_colors(current_string['id'])
            st.markdown(
                f"""
                <div class="content-container">
                    <div class="card" style="background-color: {colors['bg']};">
                        <h2 style="color: {colors['text']};">
                            {current_string['content']}
                        </h2>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            if st.button(
                "＞",
                key="next",
                disabled=st.session_state.current_index == len(
                    st.session_state.random_strings) - 1
            ):
                st.session_state.current_index += 1
                st.rerun()

        # 現在の位置を表示
        total = len(st.session_state.random_strings)
        current = st.session_state.current_index + 1
        st.markdown(f"""
        <div style='text-align: center'>
            <span class='navigation-text'>{current} / {total}</span>
        </div>
        """, unsafe_allow_html=True)

elif page == "文字列登録":
    st.header("文字列登録")

    if not st.session_state.is_admin:
        st.warning("この機能は管理者のみ使用できます。サイドバーからログインしてください。")
    else:
        # タブで個別登録とCSV登録を分ける
        tab1, tab2 = st.tabs(["個別登録", "CSV一括登録"])

        with tab1:
            with st.form("string_form", clear_on_submit=True):
                content = st.text_area("登録する文字列を入力してください", height=100)
                submitted = st.form_submit_button("登録")

                if submitted and content:
                    add_string(content)
                    st.success(f"「{content}」を登録しました！")
                    st.balloons()
                elif submitted:
                    st.error("文字列を入力してください。")

        with tab2:
            st.markdown("""
            ### CSV一括登録
            
            #### 📝 CSVファイルの形式
            - 1行目：ヘッダー行（content）
            - 2行目以降：登録する文字列（1行1文字列）
            
            #### 📄 CSVファイル例
            ```
            content
            一つ目の文字列
            二つ目の文字列
            三つ目の文字列
            ```
            """)

            # CSVファイルのサンプルをダウンロードできるようにする
            sample_csv = """content
                        一つ目の文字列
                        二つ目の文字列
                        三つ目の文字列"""

            st.download_button(
                label="📥 サンプルCSVをダウンロード",
                data=sample_csv.encode('shift-jis'),
                file_name="sample_strings.csv",
                mime="text/csv"
            )

            st.markdown("---")

            # CSVファイルのアップロード
            uploaded_file = st.file_uploader("CSVファイルを選択してください", type=['csv'])

            if uploaded_file is not None:
                try:
                    # CSVファイルの文字コードを自動判定
                    csv_data = uploaded_file.read()
                    df = None
                    encodings = ['utf-8', 'shift-jis', 'cp932']

                    for encoding in encodings:
                        try:
                            df = pd.read_csv(io.BytesIO(
                                csv_data), encoding=encoding)
                            break
                        except UnicodeDecodeError:
                            continue

                    if df is None:
                        raise ValueError("サポートされている文字コードで読み込めませんでした。")

                    if 'content' not in df.columns:
                        raise ValueError("CSVファイルに'content'列が見つかりません。")

                    # プレビューを表示
                    st.write("📋 登録予定の文字列：")
                    st.dataframe(df)

                    # 登録実行ボタン
                    if st.button("一括登録を実行", type="primary"):
                        # 空白行を除外して登録
                        valid_strings = df['content'].dropna().tolist()
                        add_multiple_strings(valid_strings)
                        st.success(f"{len(valid_strings)}件の文字列を登録しました！")
                        st.balloons()

                except (pd.errors.EmptyDataError, ValueError) as e:
                    st.error(f"CSVファイルの読み込みに失敗しました。エラー: {str(e)}")
                    st.markdown("""
                    #### 💡 よくあるエラーの解決方法
                    1. CSVファイルの文字コードを確認してください（UTF-8推奨）
                    2. ヘッダー行に'content'が含まれているか確認してください
                    3. ファイルが破損していないか確認してください
                    """)

else:  # 一覧表示
    st.header("登録済み文字列一覧")

    strings = get_all_strings()
    if strings:
        # 一括削除ボタン（管理者のみ表示）
        if st.session_state.is_admin:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🗑️ 一括削除", type="secondary"):
                    # 確認ダイアログ
                    if st.session_state.get('confirm_delete_all', False):
                        delete_all_strings()
                        st.success("全ての文字列を削除しました。")
                        st.rerun()
                    else:
                        st.session_state.confirm_delete_all = True
                        st.warning("⚠️ 本当に全ての文字列を削除しますか？もう一度クリックすると削除されます。")

            # キャンセルボタン（確認ダイアログ表示時のみ）
            if st.session_state.get('confirm_delete_all', False):
                with col1:
                    if st.button("キャンセル"):
                        st.session_state.confirm_delete_all = False
                        st.rerun()

        # 文字列一覧の表示
        for string in strings:
            with st.container():
                col1, col2 = st.columns([5, 1])
                colors = get_card_colors(string['id'])
                with col1:
                    st.markdown(f"""
                    <div class="card" style="background-color: {colors['bg']};">
                        <h2 style="color: {colors['text']};">{string['content']}</h2>
                        <small>登録日時: {string['created_at']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                # 削除ボタン（管理者のみ表示）
                if st.session_state.is_admin:
                    with col2:
                        if st.button("削除", key=f"delete_{string['id']}", type="secondary"):
                            delete_string(string['id'])
                            st.success("文字列を削除しました。")
                            st.rerun()
    else:
        st.info("登録された文字列がありません。")

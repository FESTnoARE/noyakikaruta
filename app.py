"""
のやき札アプリケーション

文字列をランダムに表示するStreamlitウェブアプリケーション
"""

# 標準ライブラリ
import hashlib
import io
# os, sqlite3 は不要なので削除

# サードパーティライブラリ
import pandas as pd
import streamlit as st

# データベースモジュールのインポート
import database as db

# 設定はst.secretsから直接読み込む
try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except KeyError:
    st.error("管理者パスワードが設定されていません。Streamlit CloudのSecretsに `ADMIN_PASSWORD` を設定してください。")
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

# データベース接続関数はdatabase.pyに移動したので削除


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
        white-space: pre-wrap; /* 改行を保持 */
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
    db.init_db()


# データベース初期化を実行
init_db()

# 文字列の登録、一括登録、取得、削除などの関数はdatabase.pyに移動したので削除

# ページごとの処理
if page == "ランダム表示":
    st.subheader("ランダム表示")

    # セッションにランダムな文字列リストがない場合は取得
    if not st.session_state.random_strings:
        df = db.get_all_strings_random()
        if not df.empty:
            st.session_state.random_strings = df.to_dict('records')

    if st.button("🔄 新しい札を引く"):
        df = db.get_all_strings_random()
        if not df.empty:
            st.session_state.random_strings = df.to_dict('records')
            st.session_state.current_index = 0
        else:
            st.session_state.random_strings = []
        st.rerun()

    if st.session_state.random_strings:
        total = len(st.session_state.random_strings)
        st.session_state.current_index = min(
            st.session_state.current_index, total - 1)

        # ナビゲーション
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("◀️ 前へ"):
                st.session_state.current_index = (
                    st.session_state.current_index - 1 + total) % total
                st.rerun()
        with col3:
            if st.button("次へ ▶️"):
                st.session_state.current_index = (
                    st.session_state.current_index + 1) % total
                st.rerun()

        # 現在の文字列データを取得
        string_data = st.session_state.random_strings[st.session_state.current_index]
        content = string_data['content']
        string_id = string_data['id']

        # 色を決定
        colors = get_card_colors(string_id)

        # 文字列をカードで表示
        st.markdown(f"""
        <div class="content-container">
            <div class="card" style="background-color:{colors['bg']}; color:{colors['text']};">
                <h2>{content}</h2>
            </div>
            <div class="navigation-text">
                {st.session_state.current_index + 1} / {total}
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.info("表示する文字列がありません。データを登録してください。")


elif page == "文字列登録":
    st.subheader("文字列登録")

    if st.session_state.is_admin:
        with st.form("add_form", clear_on_submit=True):
            new_string = st.text_area("新しい文字列を入力してください", height=150)
            if st.form_submit_button("登録する"):
                if new_string:
                    db.add_string(new_string)
                    st.success("文字列を登録しました！")
                else:
                    st.warning("文字列を入力してください。")

        st.markdown("---")
        st.subheader("CSVファイルから一括登録")

        with st.form("upload_form"):
            uploaded_file = st.file_uploader(
                "CSVファイルを選択 (UTF-8, Shift-JIS, CP932対応)", type=['csv'])
            submit_button = st.form_submit_button("プレビュー")

        if uploaded_file and submit_button:
            try:
                # 文字コードの自動判別
                encodings = ['utf-8', 'shift-jis', 'cp932']
                df = None
                for enc in encodings:
                    try:
                        uploaded_file.seek(0)
                        df = pd.read_csv(
                            uploaded_file, header=None, encoding=enc)
                        st.session_state.detected_encoding = enc
                        break
                    except Exception:
                        continue

                if df is not None:
                    st.session_state.dataframe_to_upload = df
                    st.success(
                        f"ファイルを読み込みました (文字コード: {st.session_state.detected_encoding})。")
                    st.write("プレビュー:")
                    st.dataframe(df)
                else:
                    st.error("ファイルの読み込みに失敗しました。対応する文字コードのファイルか確認してください。")

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

        if 'dataframe_to_upload' in st.session_state and not st.session_state.dataframe_to_upload.empty:
            if st.button("この内容でデータベースに一括登録する"):
                try:
                    string_list = st.session_state.dataframe_to_upload.iloc[:, 0].dropna().astype(
                        str).tolist()
                    if string_list:
                        db.add_multiple_strings(string_list)
                        st.success(f"{len(string_list)}件の文字列を一括登録しました！")
                    else:
                        st.warning("登録するデータがありません。")
                except Exception as e:
                    st.error(f"データベースへの登録中にエラーが発生しました: {e}")
                finally:
                    # 処理後にセッション状態をクリア
                    del st.session_state.dataframe_to_upload
                    if 'detected_encoding' in st.session_state:
                        del st.session_state.detected_encoding
                    st.rerun()

        st.markdown("---")
        st.markdown("##### サンプルCSV")
        sample_df = pd.DataFrame(["一行目の内容", "二行目の内容", "三行目の内容"])
        csv = sample_df.to_csv(index=False, header=False).encode('utf-8')
        st.download_button(
            label="サンプルCSVをダウンロード",
            data=csv,
            file_name="sample.csv",
            mime="text/csv",
        )

    else:
        st.warning("この機能は管理者専用です。")

elif page == "一覧表示":
    st.subheader("登録済み文字列一覧")

    all_strings_df = db.get_all_strings()

    if not all_strings_df.empty:
        if st.session_state.is_admin:
            # 管理者向け: 削除ボタン付き
            st.info("削除したい項目がある場合は、IDを指定して削除してください。")
            with st.form("delete_form"):
                delete_id = st.number_input("削除するID", min_value=1, step=1)
                if st.form_submit_button("🗑️ 指定したIDを削除"):
                    try:
                        db.delete_string(delete_id)
                        st.success(f"ID:{delete_id}を削除しました。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"削除中にエラーが発生しました: {e}")

            st.markdown("---")
            st.subheader("⚠️ すべてのデータを削除")
            if st.button("すべてのデータを削除する", type="primary"):
                if 'confirm_delete_all' not in st.session_state:
                    st.session_state.confirm_delete_all = True
                    st.rerun()
                # 2回目に押されたら削除を実行
                else:
                    db.delete_all_strings()
                    del st.session_state.confirm_delete_all
                    st.success("すべてのデータを削除しました。")
                    st.rerun()

            if st.session_state.get('confirm_delete_all'):
                st.warning("本当によろしいですか？この操作は取り消せません。もう一度上のボタンを押すと削除が実行されます。")
                if st.button("キャンセル"):
                    del st.session_state.confirm_delete_all
                    st.rerun()

        st.markdown("---")
        # DataFrameをHTMLに変換して表示
        for index, row in all_strings_df.iterrows():
            st.markdown(f"""
            <div class="card">
                ID: {row['id']} | 登録日時: {pd.to_datetime(row['created_at']).strftime('%Y-%m-%d %H:%M')}
                <p style="font-size: 1.2em; margin-top: 5px;">{row['content']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("登録されている文字列はありません。")

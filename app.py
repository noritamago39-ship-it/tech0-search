#起動： streamlit run app.py 
import streamlit as st
from database import init_db, insert_page, get_all_pages,migrate_from_json
from ranking import get_engine,rebuild_index #w4のTF-IDF 検索 
from crawler import crawl_url  # W2 から流用

# アプリ起動時に DB を初期化する（テーブルが未作成なら作る）
init_db()


# ── ③ ページ設定・タイトル ──
st.set_page_config(page_title="Tech0 Search v1.0", page_icon="🔍")
st.title("🔍 Tech0 Search v1.0")
st.caption("PROJECT ZERO — 社内ナレッジ検索エンジン")

#---キャッシュ付インデックス構築---
@st.cache_resource
def load_and_index():
    pages = get_all_pages()
    if pages:
        rebuild_index(pages)
    return pages

pages = load_and_index()
engine = get_engine()

# サイドバー:pages_w2.json →DBへの移行(w3の移行作業)
with st.sidebar:
    st.header("DBの状態")

    #st.rerun()をまたいでメッセージを持ち越す（w1と同じ仕組み）
    if st.session_state.get("migrated") is not None:
        st.success(f"{st.session_state['migrated']} 件を DB に移行しました")
        st.session_state["migrated"] = None
    pages= get_all_pages()
    st.metric("登録ページ数", f"{len(pages)}件")
    if st.button("📦 pages_w2.json から DB へ移行"):
        n = migrate_from_json("pages_w2.json")
        st.session_state["migrated"] = n #件数を印として残す
        st.cache_resource.clear()
        st.rerun()


# ── ④ タブを作る ──
tab1, tab2, tab3 = st.tabs(["検索", "クロール", "一覧"])

# ── ⑤ 検索タブ （DB → 全文検索の2行がキモ） ──
with tab1:
    st.subheader("🔍 全文検索（本文まで探す）")
    query = st.text_input("🔑 キーワードを入力")
    if query:
        results = engine.search(query) #④シェフに聞く（TF-IDF で並べる）

        st.markdown(f"**検索結果：{len(results)}件**(TF-IDFスコア順)")
        st.divider()
        for i,r in enumerate(results,1):   #①順位の番号iも一緒にもらう
            medal = ["🥇", "🥈", "🥉"][i-1]if i <=3 else str(i) #②上位3位はメダル、4位からは数字を返す      
            st.markdown(f"### {medal} [{r['title']}]({r['url']})")#③タイトルの前にメダルを出す            
            st.markdown(f"📊 スコア: **{r['relevance_score']}**(基準：{r['base_score']})")
            if r.get("description"):
                st.caption(r["description"])
            st.divider()
            

# ── クロールタブ ──
with tab2:
    st.subheader("🤖 自動クローラー")
#    # 単体クロール
    st.markdown("**単体クロール**")
    if st.session_state.get("crawled") is not None: #メモがあれば
        st.success(f"✅ 取得成功:{st.session_state['crawled']}(DBに登録しました)")
        st.session_state["crawled"] = None #出したらメモを消す
    url_input = st.text_input("クロールしたいURL")
    if st.button("クロール実行"):
       if url_input:
            with st.spinner(f"クロール中: {url_input}"):
             result = crawl_url(url_input)
            if result.get("crawl_status") == "success":
                st.success(f"✅ 取得成功: {result['title']}")
                st.caption(f"📊 {result['word_count']} 語 ／ 🔗  リンク {len(result['links'])}")
                insert_page(result)
                st.cache_resource.clear()
                st.session_state["crawled"] = result["title"]
                st.rerun()
            else:
                st.error(f"❌ 取得失敗: {result.get('error')}")

    st.divider()

    # 一括クロール
    st.markdown("**一括クロール**（URLを改行区切りで入力）")
    urls_text = st.text_area("URLリスト", height=120)
    if st.button("📋 一括クロール実行"):
        urls = [u.strip() for u in urls_text.splitlines() if u.strip().startswith("http")]
        if not urls:
            st.error("有効なURLが見つかりませんでした")
        else:
            ok = 0
            for u in urls:
                with st.spinner(f"クロール中: {u}"):
                        result = crawl_url(u)
                if result.get("crawl_status") == "success":
                        insert_page(result)
                        ok += 1
                        st.success(f"✅ {result['title']}")
                else:
                        st.error(f"❌ 失敗: {u}")
            st.info(f"{ok} / {len(urls)} 件をDBに登録しました")
            st.cache_resource.clear()
                   

# ── ⑦ 一覧タブ ──
with tab3:
    pages = get_all_pages()
    st.subheader(f"📚 登録済みページ一覧（{len(pages)}件）")
    for page in pages:
        with st.expander(f"📄 {page['title']}"):       
            st.markdown(page.get("description", "") or "（説明なし）")
            st.caption(f"👤 {page.get('author') or  '不明'}  📊 {page.get('word_count', '-')} 語")
            st.caption(f"🔗 {page['url']}")

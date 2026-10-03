def _make_preview(text:str, query:str, ctx:int = 80)-> str:
    """
    マッチ箇所周辺のプレビューを生成する。

    Args:
        text:  本文
        query:検索キーワード
        ctx:前後に表示する文字数
    
    Returns:
        preview文字列
    """

    #text   または  query が空なら空文字を返す
    if not text or not query:
        return ""

    #キーワードの位置を探す
    pos = text.lower().find(query.lower())

    #見つからない場合は先頭200文字を返す
    if pos == -1:
        return(text[:200] + "...") if len(text) >200 else text

    #前後の切り出し範囲
    start = max(0, pos- ctx)  
    end = min(len(text),pos + len(query) + ctx)

    preview = ""

    if start >0:
        preview += "..."

    preview += text[start:end]

    if end <len(text):
        preview +="..."

    return preview     

def search_fulltext(query:str, pages:list) -> list:
    """
    全文検索（本文含む）を実行し、マッチ数でスコアリングする。

    Args:
        query:検索キーワード
        pages:ページリスト

    Returns:
        マッチしたページのリスト（スコア降順）
    """

    #空文字なら空リストを返す
    if not query.strip():
        return[]

    results = []

    #検索キーワードを小文字化
    q = query.lower()

    #全ページを順番に確認
    for page in pages:

        #検索対象テキストを作る
        text = "    ".join([
            page.get("title",""),
            page.get("description",""),
            page.get("full_text",""),
            " ".join(page.get("keywords",[])),
        ]) .lower()    

        #　出現回数を数える
        count = text.count(q)

        #　ヒットしたページだけ追加
        if count > 0:

            r = page.copy()

            #match_countを追加
            r["match_count"] = count

            #previewを追加
            r["preview"] = _make_preview(
                page.get("full_text") or page.get("description",""),
                query
            )

            results.append(r)

    #match_count順に並べる
    results.sort(key=lambda x: x["match_count"],reverse=True)

    return results

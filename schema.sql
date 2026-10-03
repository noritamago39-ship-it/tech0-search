--schema.sql
-- Tech0 Search データベース設計（w3:データ基盤の最小構成）

CREATE TABLE IF NOT EXISTS pages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    url         TEXT NOT NULL UNIQUE,
    title       TEXT NOT NULL,
    description TEXT,
    full_text   TEXT,
    author      TEXT,
    category    TEXT,
    keywords    TEXT,
    word_count  INTEGER DEFAULT 0,
    crawled_at  DATETIME,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- keywordsテーブル（TF-IDFスコア保存用。実際に使うのは W4）
CREATE TABLE IF NOT EXISTS keywords(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id     INTEGER NOT NULL,
    keyword     TEXT NOT NULL,
    tf_score    REAL DEFAULT 0.0,
    tfidf_score REAL DEFAULT 0.0,
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
);

--インデックス作成（検索を高速化する）
CREATE INDEX IF NOT EXISTS idx_keyword ON keywords(keyword);
CREATE INDEX IF NOT EXISTS idx_page_id ON keywords(page_id);

        
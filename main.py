# --- 必要な道具（ライブラリ）を読み込む ---
from urllib.parse import urljoin  # URLを綺麗につなぎ合わせるための道具
from bs4 import BeautifulSoup  # ウェブページのHTMLを解析するための道具
from feedgen.feed import FeedGenerator  # RSS（XML）ファイルを作るための道具
import requests  # ウェブサイトにアクセスしてデータを取ってくるための道具


def main():
  # 1. 取得したいターゲットのURL（OLDFISHのお知らせページ）
  target_url = "https://www.oldfish.jp/view/news/list"

  # 2. アクセスするときに「普通のパソコンのブラウザから見に来たよ」と偽装する設定
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }

  # 3. 指定したURLにアクセスして、ページのHTMLデータを丸ごとダウンロードする
  response = requests.get(target_url, headers=headers)
  response.encoding = response.apparent_encoding  # 文字化けを防ぐ設定
  soup = BeautifulSoup(
      response.text, "html.parser"
  )  # ダウンロードしたHTMLを解析しやすくする

  # 4. RSSフィード（自分用の更新情報ファイルの土台）を作る
  fg = FeedGenerator()
  fg.title("OLDFISH お知らせ・更新情報")  # RSSのタイトル
  fg.link(href=target_url, rel="alternate")  # 元サイトのリンク
  fg.description(
      "OLDFISHのお知らせ一覧から自動生成したRSSフィード"
  )  # RSSの説明文
  fg.language("ja")  # 言語設定（日本語）

  # 5. ページの中にあるすべての「リンク（<a>タグ）」を順番に探す
  news_links = soup.find_all("a", href=True)
  added_urls = set()  # 同じニュースが何度も登録されないようにするためのメモ帳

  # 見つかったリンクを1つずつチェックしていく
  for a in news_links:
    href = a["href"]  # リンク先のURLを取得

    # リンクの中に「/view/news/」（お知らせの個別ページ）が含まれていて、まだ登録していなかったら処理する
    if "/view/news/" in href and href not in added_urls:
      added_urls.add(href)  # 「登録済み」としてメモする

      title = a.get_text(strip=True)  # リンクの文字（お知らせのタイトル）を取り出す

      # もしタイトルが空っぽだったり、単なる「お知らせ一覧」という文字だったらスキップする
      if not title or title == "お知らせ一覧":
        continue

      # 相対URL（/view/news/...）を、完全なURL（https://...）に変換する
      full_url = urljoin("https://www.oldfish.jp", href)

      # リンクの親要素（まわりの部分）から日付などのテキストがあれば取得する
      parent_text = a.parent.get_text(strip=True) if a.parent else ""

      # --- RSSの中に1記事分のデータとして書き込む ---
      fe = fg.add_entry()
      fe.title(title)  # 記事のタイトル
      fe.link(href=full_url)  # 記事のリンク
      fe.guid(full_url, permalink=True)  # 記事の固有ID（リンクを使う）

      # 日付や詳細のテキストがあれば、RSSの説明欄（本文）に入れる
      if parent_text:
        fe.description(parent_text)

  # 6. 集めたデータをまとめて「oldfish.xml」という名前のRSSファイルとして保存する
  fg.rss_file("oldfish.xml")
  print("oldfish.xml の作成が完了しました。")


# このスクリプトが直接実行されたときに main() 関数を動かすお決まりの記述
if __name__ == "__main__":
  main()

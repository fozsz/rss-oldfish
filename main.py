# --- 必要なライブラリの読み込み ---
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import requests


def main():
  # 1. OLDFISHの「新着順」検索結果ページに変更
  target_url = "https://www.oldfish.jp/view/search?sort=order"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }

  # 2. ページHTMLの取得
  response = requests.get(target_url, headers=headers)
  response.encoding = response.apparent_encoding
  soup = BeautifulSoup(response.text, "html.parser")

  # 3. RSSの土台作成
  fg = FeedGenerator()
  fg.title("OLDFISH 新着商品")
  fg.link(href=target_url, rel="alternate")
  fg.description(
      "OLDFISH（https://www.oldfish.jp/）の新着商品自動生成RSSフィード"
  )
  fg.language("ja")

  # 4. 商品一覧のカード要素（または商品名リンク）を抽出
  # Makeshop等のECカートシステムでは、商品リンクは通常 /view/item/ 形式になっています
  items = soup.find_all("a", href=True)
  added_urls = set()

  for a in items:
    href = a["href"]

    # 商品ページ（/view/item/）のリンクだけを正確に狙う
    if "/view/item/" in href and href not in added_urls:
      # 商品名や画像altなどからタイトルを綺麗に取得する
      title = a.get_text(strip=True)

      # もしリンクの中に画像があってテキストが空の場合、画像のalt属性をタイトル代わりに救出する
      if not title:
        img = a.find("img")
        if img and img.get("alt"):
          title = img["alt"]

      if not title:
        continue

      full_url = urljoin(target_url, href)

      # 重複を防ぐためセットに追加
      added_urls.add(href)

      # RSSエントリーの追加
      fe = fg.add_entry()
      fe.title(title)
      fe.link(href=full_url)
      fe.guid(full_url, permalink=True)

  # 5. oldfish.xml ファイルとして保存
  fg.rss_file("oldfish.xml")
  print("oldfish.xml の作成が完了しました（新着順ページベース）。")


if __name__ == "__main__":
  main()

"""
Scraping ulasan Google Play Store (Gojek) -> dataset_ulasan_gojek.csv

Jalankan:  python scraping.py
Kolom username sengaja tidak disimpan (tidak dibutuhkan untuk analisis).
"""
import time

import pandas as pd
from google_play_scraper import Sort, reviews

APP_ID = "com.gojek.app"      # ganti kalau mau aplikasi lain
LANG, COUNTRY = "id", "id"
PER_SCORE = 4000              # target per bintang (1-5) -> total mentah ~20.000
OUTPUT = "dataset_ulasan_gojek.csv"


def scrape_by_score(score, target):
    """Ambil ulasan dengan rating tertentu sampai `target` atau habis."""
    rows, token = [], None
    while len(rows) < target:
        batch, token = reviews(
            APP_ID,
            lang=LANG,
            country=COUNTRY,
            sort=Sort.NEWEST,
            count=200,
            filter_score_with=score,
            continuation_token=token,
        )
        rows.extend(batch)
        print(f"  rating {score}: {len(rows)} ulasan")
        if token is None or not batch:
            break
        time.sleep(1)  # jangan agresif ke server
    return rows


def main():
    all_rows = []
    for score in range(1, 6):
        print(f"Scraping rating {score} ...")
        all_rows.extend(scrape_by_score(score, PER_SCORE))

    df = pd.DataFrame(all_rows)[["reviewId", "content", "score", "thumbsUpCount", "at"]]
    df = df.rename(columns={"content": "ulasan", "score": "rating", "at": "tanggal"})
    df = df.dropna(subset=["ulasan"]).drop_duplicates(subset="reviewId")
    df = df.drop_duplicates(subset="ulasan").reset_index(drop=True)

    df.to_csv(OUTPUT, index=False)
    print(f"\nSelesai: {len(df)} ulasan unik disimpan ke {OUTPUT}")
    print(df["rating"].value_counts().sort_index())


if __name__ == "__main__":
    main()

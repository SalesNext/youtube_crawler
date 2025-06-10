# Yêu cầu để chạy (Requirements)

Trên môi trường local cần có:

- Python version: ^3.9 trở lên
- Poetry
- Đã thêm ssh vào git: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account

  Cài ssh là để có thể install được package nội bộ của công ty: `salesnext-crawler`

# Cài đặt (Installation)

```bash
git init
make install
```

Câu lệnh `make install` trên sẽ cài các package khởi tạo cho project (`poetry install`), đồng thời cài đặt pre-commit (`poetry run pre-commit install` ).

# Chạy (How to run)

company:

```
poetry run salesnext-crawler crawl config-company.toml
```

company realtime:

```
poetry run salesnext-crawler crawl config-new-company.toml
```

job:

```
poetry run salesnext-crawler crawl config-job.toml
```

job realtime:

```
poetry run salesnext-crawler crawl config-new-jobs.toml
```
# youtube-crawler
# youtube_crawler
# youtube_crawler

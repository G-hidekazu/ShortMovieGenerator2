# ShortMovieGenerator2

YouTube動画のURL（または動画ID）を渡すと、字幕から重要なセリフを3つ抽出し、それぞれに簡潔な解説を付けて表示するWebアプリです。CLIも引き続き利用できます。

## セットアップ

```bash
pip install -r requirements.txt
```

## 使い方

```bash
flask --app short_movie_generator.web_app:app run
```

ブラウザで http://127.0.0.1:5000/ を開き、動画URL（または動画ID）と字幕の優先言語（スペース区切り）を入力すると、重要なセリフ3つと解説が表示されます。字幕が取得できない場合はエラーメッセージが表示されます。

## CLIとして使う場合

```bash
python -m short_movie_generator.cli "https://www.youtube.com/watch?v=VIDEO_ID"
```

オプション:

- `--lang ja en` のように指定すると、字幕取得で優先する言語の順序を変更できます（デフォルトは `ja en`）。

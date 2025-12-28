# ShortMovieGenerator2

YouTube動画のURL（または動画ID）を渡すと、字幕を取得して全文を表示するWebアプリです。CLIも利用できます。

## セットアップ

依存ライブラリを最新化してから利用してください。特に `youtube-transcript-api` は **0.6.2 以上** へのアップグレードが必要です。

```bash
pip install --upgrade youtube-transcript-api
pip install -r requirements.txt
```

## 使い方

```bash
flask --app short_movie_generator.web_app:app run
```

ブラウザで http://127.0.0.1:5000/ を開き、動画URL（または動画ID）と字幕の優先言語（スペース区切り）を入力すると、取得した字幕を順番に表示します。字幕が取得できない場合はエラーメッセージが表示されます。

## CLIとして使う場合

```bash
python -m short_movie_generator.cli "https://www.youtube.com/watch?v=VIDEO_ID"
```

オプション:

- `--lang ja en` のように指定すると、字幕取得で優先する言語の順序を変更できます（デフォルトは `ja en`）。

# Gaica Export

How to run

1. Save GAICA 明細書 HTML files to a folder
2. Run `pipenv run ./convert.py $INPUT_FOLDER $OUTPUT_CSV`

Fancy people do

```
pipenv shell
# in fish
./convert.py $SOME_FOLDER/gaica/{in/,out/(date +'%F').csv}
```

## Installation

Use pipenv.

```
pipenv install
```

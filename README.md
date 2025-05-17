# Git LOC Plot

Plot lines of code over time in a Git repository

Counts the lines of codes in each commit in the current branch. Outputs two files; a .csv file with LOC data, and a .png image visualizing lines of code per language over time.

## Dependencies
- [cloc](https://github.com/AlDanial/cloc) `sudo apt install cloc`
- pandas `pip install pandas`
- matplotlib `pip install matplotlib`

## Usage

Basic usage:

```
python loc.py <path-to-repo> --langs=Java
```

Use `--langs` to filter the output to one or more languages

The option takes a comma-separated list of languages supported by cloc. To see supported languages: `clocl -show-lang`.

```
python loc.py <path-to-repo> --langs=Java
```


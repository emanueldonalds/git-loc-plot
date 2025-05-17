import os
import subprocess
import tempfile
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def count_loc(repo_path, csv_path, langs):
    commits = (
        subprocess.check_output(["git", "rev-list", "HEAD"], cwd=repo_path)
        .decode()
        .splitlines()
    )
    n_commits = len(commits)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        for i, commit in enumerate(commits, 1):
            raw_date = (
                subprocess.check_output(
                    ["git", "log", commit, "--pretty=format:%ci", "-n1"], cwd=repo_path
                )
                .decode()
                .strip()
            )

            cmt_date = (
                subprocess.check_output(["date", "-d", raw_date, "--iso-8601=seconds"])
                .decode()
                .strip()
            )

            cloc_args = ["cloc", commit, "--git", "--vcs=git", "--csv"]
            if langs:
                cloc_args.append(f"--include-lang={langs}")

            cloc_output = (
                subprocess.check_output(
                    cloc_args, cwd=repo_path
                )
                .decode()
                .splitlines()
            )

            data_lines = cloc_output[1:-1]
            for line in data_lines:
                row = f"{cmt_date},{line}"
                temp_file.write(row + "\n")

            print(f"\rCounting LOC in commit {commit} [{i} / {n_commits}] ", end="")

    os.replace(temp_file.name, csv_path)

def plot(csv_path, png_path):
    df = pd.read_csv(csv_path, header=None, names=["date", "files", "language", "blank", "comment", "code"])

    df["date"] = pd.to_datetime(df["date"], utc=True)

    grouped = df.groupby(["date", "language"])["code"].max().unstack(fill_value=0)
    grouped = grouped.sort_index()

    plt.figure(figsize=(14, 7))
    for language in grouped.columns:
        plt.plot(grouped.index, grouped[language], label=language)

    plt.title("Lines of Code per Language Over Time")
    plt.xlabel("Date")
    plt.ylabel("Lines of Code")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()

    plt.savefig(png_path)
    print(f"Plot saved to {png_path}")

def main():
    parser = argparse.ArgumentParser(description="Count lines of code per commit.")
    parser.add_argument("repo", help="Path to the Git repository")
    parser.add_argument("--outdir", default=".", help="Path to the directory where output files will be saved")
    parser.add_argument("--langs", default="", help="Path to the directory where output files will be saved")
    args = parser.parse_args()

    repo_path = Path(args.repo).resolve()
    if not (repo_path / ".git").is_dir():
        print(f"Error: {repo_path} is not a valid Git repository.")
        return

    repo_name = repo_path.name

    csv_path = f"{args.outdir}/loc_{repo_name}.csv"
    png_path = f"{args.outdir}/loc_{repo_name}.png"

    count_loc(repo_path, csv_path, args.langs)
    plot(csv_path, png_path)

    print(f"\nDone! Output written to [{csv_path}] and [{png_path}]")


if __name__ == "__main__":
    main()

import os
from datetime import datetime
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
    loc_files = []
    df = pd.DataFrame()

    with tempfile.TemporaryDirectory(delete=False) as temp_dir:
        for i, commit in enumerate(commits, 1):
            print(f"\rCounting LOC in commit {commit} [{i} / {n_commits}] ", end="")

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

            loc_file = os.path.join(temp_dir, f"{cmt_date}.csv")
            cloc_args = ["cloc", commit, "--git", "--vcs=git", "--csv", f"--report-file={loc_file}"]

            if langs:
                cloc_args.append(f"--include-lang={langs}")

            subprocess.run(cloc_args, cwd=repo_path, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if not os.path.exists(loc_file):
                print(f"\nWarning: cloc did not produce any output for commit {commit}")
                continue

            loc_files.append(loc_file)

        # merge partial files together to a single table
        for file in loc_files:
            partial_df = pd.read_csv(file)

            # Don't want the generated SUM row
            partial_df = partial_df[partial_df["language"] != "SUM"]

            date = os.path.basename(file)
            date = str.split(date, ".")[0]
            date = datetime.fromisoformat(date)
            partial_df["date"] = date
            partial_df = partial_df[["date", "language", "code"]]
            
            df = pd.concat([df, partial_df], ignore_index=True)

    df.to_csv(csv_path, index=False)
    return df

def plot(df, png_path):
    grouped = df.groupby(["date", "language"])["code"].max().unstack(fill_value=0)
    grouped = grouped.sort_index()

    plt.figure(figsize=(14, 7))
    for language in grouped.columns:
        plt.plot(grouped.index, grouped[language], label=language)

    #plt.title("Lines of code over time")
    plt.xlabel("Date")
    plt.ylabel("Lines of Code")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()

    plt.savefig(png_path)

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

    csv_path = os.path.join(args.outdir, f"loc_{repo_name}.csv")
    png_path = os.path.join(args.outdir, f"loc_{repo_name}.png")

    df = count_loc(repo_path, csv_path, args.langs)
    plot(df, png_path)

    print(f"\nOutput written to:\n{csv_path}\n{png_path}")


if __name__ == "__main__":
    main()

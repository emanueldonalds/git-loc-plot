import os
import subprocess
import tempfile
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def count_loc(repo_path, outdir):
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

            cloc_output = (
                subprocess.check_output(
                    ["cloc", commit, "-q", "--git", "--csv"], cwd=repo_path
                )
                .decode()
                .splitlines()
            )

            data_lines = cloc_output[2:-1]
            for line in data_lines:
                row = f"{cmt_date},{line}"
                temp_file.write(row + "\n")

            print(f"\rCounting LOC in commit {commit} [{i} / {n_commits}] ", end="")

    csv_outfile = f"{outdir}/loc.csv"
    os.replace(temp_file.name, csv_outfile)
    print(f"\nDone! Output written to {csv_outfile}")
    return csv_outfile

def plot(csv_file):
    df = pd.read_csv(csv_file, header=None, names=["date", "files", "language", "blank", "comment", "code"])

    df["date"] = pd.to_datetime(df["date"], utc=True).dt.date

    grouped = df.groupby(["date", "language"])["code"].sum().unstack(fill_value=0)
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

    output_path = Path.home() / "loc.png"
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Count lines of code per commit.")
    parser.add_argument("repo", help="Path to the Git repository")
    parser.add_argument("--outdir", default=".", help="Path to the directory where output files will be saved")
    args = parser.parse_args()

    repo_path = Path(args.repo).resolve()
    if not (repo_path / ".git").is_dir():
        print(f"Error: {repo_path} is not a valid Git repository.")
        return

    csv_file = count_loc(repo_path, args.outdir)
    plot(csv_file)


if __name__ == "__main__":
    main()

"""Bytes, lines and proxy token counts of files in a repo at a commit (CE-4 baseline, CE-7 scoring).

Run: `<interpreter> tools/count_context.py <repo> <sha> <path> [<path> ...]`. Reads with
`git show`, so it never touches the target's working tree.

Tokens are PROXIES; Claude's tokenizer has no local release, and an exact Claude count needs the
token-counting API and a key. Two proxies give a spread:
- `tiktoken`: OpenAI's `o200k_base` (`pip install tiktoken`);
- `gemma`: Vertex AI's local tokenizer for `gemini-1.5-pro`, Gemma's sentencepiece model,
  downloaded once without a key (`pip install "google-cloud-aiplatform[tokenization]"`).
Use the same proxies on both arms of a comparison. Neither is an engine dependency.
"""
import subprocess, sys

import tiktoken
from vertexai.preview.tokenization import get_tokenizer_for_model

ENCODING = "o200k_base"
GEMMA_MODEL = "gemini-1.5-pro"


def show(repo, sha, path):
    return subprocess.run(["git", "-C", repo, "show", f"{sha}:{path}"],
                          capture_output=True, check=True).stdout


def main(repo, sha, *paths):
    enc = tiktoken.get_encoding(ENCODING)
    gemma = get_tokenizer_for_model(GEMMA_MODEL)
    print(f"# {repo} @ {sha}; tiktoken = {ENCODING}, gemma = vertexai {GEMMA_MODEL} (proxies)")
    print("path\tbytes\tlines\ttiktoken\tgemma")
    for p in paths:
        raw = show(repo, sha, p)
        text = raw.decode("utf-8")
        print(f"{p}\t{len(raw)}\t{text.count(chr(10))}"
              f"\t{len(enc.encode(text, disallowed_special=()))}\t{gemma.count_tokens(text).total_tokens}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])

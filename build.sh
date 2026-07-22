#!/usr/bin/env bash
set -e

# 1. 先构建 Hugo，生成 public/
hugo --minify

# 2. 遍历 books/ 下每个子目录，构建进 public/books/<name>
for dir in books/*/; do
  name=$(basename "$dir")
  mkdir -p "public/books/$name"
  npx honkit build "$dir" "public/books/$name"
done
#!/usr/bin/env bash
set -eu
mkdir -p inputs work
for f in "$(dirname "$0")"/files/*; do
  case "$(basename "$f")" in
    menu_current.json) cp "$f" work/ ;;
    *) cp "$f" inputs/ ;;
  esac
done

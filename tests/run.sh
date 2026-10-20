#!/usr/bin/env bash
# Compila o núcleo (Kotlin puro) + testes e roda. Uso: tests/run.sh <pasta com kotlinc/ e json.jar>
set -e
T=${1:-/tmp/claude-0/-home-user-teste-3/400edce2-80ea-57f6-97f9-c6ff24db5c18/scratchpad}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT=$T/build-tests
mkdir -p "$OUT"
CP="$T/json.jar:$T/kotlinc/lib/kotlinx-coroutines-core-jvm.jar"
if ! "$T/kotlinc/bin/kotlinc" -nowarn -cp "$CP" -d "$OUT/t.jar" "$ROOT"/app/src/main/java/com/forja/app/core/*.kt "$ROOT"/tests/*.kt 2>&1 | grep -v "^warning"; then :; fi
[ -f "$OUT/t.jar" ] || { echo "COMPILAÇÃO FALHOU"; exit 1; }
java -Dstdout.encoding=UTF-8 -Dfile.encoding=UTF-8 -cp "$OUT/t.jar:$CP:$T/kotlinc/lib/kotlin-stdlib.jar" TesteNucleoKt "$ROOT/app/src/main/assets/exercises.json" "${@:2}"

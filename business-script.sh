#!/bin/bash
PAGE_RANGE="1"
OUTDIR="./tabula_output"
mkdir -p "$OUTDIR"

TABULA_JAR="./tabula-1.0.5-jar-with-dependencies.jar"

for year in {2018..2022}; do
    find "./$year" -type f -name "POWER*.pdf" -print0 | while IFS= read -r -d '' pdf; do
        base=$(basename "$pdf" .pdf)
        echo "Tabula'ing $pdf..."
        /usr/lib/jvm/java-8-openjdk/bin/java -Dfile.encoding=utf-8 \
            -Xms256M -Xmx1024M \
            -jar "$TABULA_JAR" --guess -t -p "$PAGE_RANGE" \
            -o "$OUTDIR/${base}.csv" "$pdf"
    done
done

echo "Extracted CSVs are in $OUTDIR"

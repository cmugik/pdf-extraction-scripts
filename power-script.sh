#!/bin/bash
OUTDIR="./tabula_output"
mkdir -p "$OUTDIR"

TABULA_JAR="./tabula-1.0.5-jar-with-dependencies.jar"
AREA_PAGE1="416.835495,66.9375,730.485495,437.9625"
AREA_PAGE2="176.98275,72.152505,753.02775,441.647505"
for year in {2018..2022}; do
    find "./$year" -type f -name "POWER*.pdf" -print0 | while IFS= read -r -d '' pdf; do
        base=$(basename "$pdf" .pdf)
        echo "Tabula'ing $pdf..."

        # P1
        java -Dfile.encoding=utf-8 \
            -Xms256M -Xmx1024M \
            -jar "$TABULA_JAR" \
            -t \
            -a "$AREA_PAGE1" \
            -p 1 \
            -o "$OUTDIR/${base}_p1.csv" \
            "$pdf"

        # P2
        java -Dfile.encoding=utf-8 \
            -Xms256M -Xmx1024M \
            -jar "$TABULA_JAR" \
            -t \
            -a "$AREA_PAGE2" \
            -p 2 \
            -o "$OUTDIR/${base}_p2.csv" \
            "$pdf"
    done
done

echo "Extracted CSVs are in $OUTDIR"

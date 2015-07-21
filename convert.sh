#!/bin/bash
latexmk -pdf *.tex

for i in $(ls *.pdf); do
    basefilename=$(basename "$i" .pdf)
    convert -density 300 "$i" "$basefilename".png
done

latexmk -c
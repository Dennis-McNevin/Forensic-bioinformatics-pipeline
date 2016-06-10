#!/bin/bash

INPUT=$1
YSTR=$2
CODIS=$3

echo "Input VCF ${INPUT}"
echo "Y-chrom STR loci file ${YSTR}"
echo "CODIS loci file ${CODIS}"

CMD="intersectBed -a ${INPUT} -b /home/ngsforensics/forensicsapp/lobSTR_ystr_hg19.bed -wa -wb | cut -f 1,2,10,14- | sed 's/:/\t/g' | cut -f 1,2,4,8,13- | sed 's/\//\t/' | cut -f 4 --complement | awk '{print \$0 \"\t\" \$6+\$4/\$5}' > ${YSTR}"

# CMD="intersectBed -a $SAMPLE. -b ../lobSTR_ystr_hg19.bed -wa -wb | cut -f 1,2,10,14- | sed 's/:/\t/g' | cut -f 1,2,4,8,13- | sed 's/\//\t/' | cut -f 4 --complement | awk '{print \$0 \"\t\" \$6+\$4/\$5}' > $SAMPLE.ystr.txt"
echo [$CMD] `date`
eval "$CMD"

CMD="intersectBed -a ${INPUT} -b /home/ngsforensics/forensicsapp/lobSTR_codis_hg19.bed -wa -wb | cut -f 1,2,10,14- | sed 's/:/\t/g' | cut -f 1,2,4,8,13- | sed 's/\//\t/' | awk '{print \$0 \"\t\" \$7+\$4/\$6 \"\t\" \$7+\$5/\$6}'> ${CODIS}"
#CMD="intersectBed -a $SAMPLE.vcf -b ../lobSTR_codis_hg19.bed -wa -wb | cut -f 1,2,10,14- | sed 's/:/\t/g' | cut -f 1,2,4,8,13- | sed 's/\//\t/' | awk '{print \$0 \"\t\" \$7+\$4/\$6 \"\t\" \$7+\$5/\$6}'> $SAMPLE.codis.txt"
echo [$CMD] `date`
eval "$CMD"


    

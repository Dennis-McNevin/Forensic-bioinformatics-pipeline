#!/bin/bash

INPUT=$1
AI=$2
II=$3

echo "Input VCF ${INPUT}"
echo "Ancenstry Informative ${AI}"
echo "Identity Informative ${II}"

CMD="grep -P '^#' ${INPUT} > $AI"
echo [$CMD] `date`
eval "$CMD"

CMD="grep -P '^#' ${INPUT} > $II"
echo [$CMD] `date`
eval "$CMD"

CMD="intersectBed -a /home/ngsforensics/snp_panels/AIMv1.20140429.Designed.bed -b ${INPUT} -wb | /home/ngsforensics/forensicsapp/ibed2vcf.pl >> $AI"
echo [$CMD] `date`
eval "$CMD"

CMD="intersectBed -a /home/ngsforensics/snp_panels/IISNPv3.20140429.Designed.bed -b ${INPUT} -wb | /home/ngsforensics/forensicsapp/ibed2vcf.pl >> $II"
echo [$CMD] `date`
eval "$CMD"

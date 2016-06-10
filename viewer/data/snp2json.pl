#!/usr/bin/env perl
use Data::Dumper;
use List::Util qw(sum);

my %primaryThresh=();
my %stutterThresh=();

#open IN,"threshold.csv" or die "unable to open threshold.csv file in results directory";
#while(<IN>) {
#	chomp;
#	my($locus,$type,$t,$s)=split/,/; #comma-delimited!
#	$primaryThresh{$locus}=$t;
#	$stutterThresh{$locus}=$s;
#}
my %json=();
for my $origname(@ARGV) {
		$json='';
		@snps=();
		$type="SNP";
		%unlisted=();
		$filename=$origname;
		$filename=~s/\.(codis|ystr)\.txt$/.\1/;
		my($sample,$type)=split/\./,$filename;
		open IN,$origname or die;
		while(<IN>) {
#chr1	12608177	12608178	rs6541030	ai	5	10	5	;	chr1	12608178	.	A	G	222	.	DP=7890;VDB=9.341664e-17;RPB=1.584304e+00;AF1=1;AC1=2;DP4=5,2,5955,1916;MQ=60;FQ=-282;PV4=0.68,0.13,0.46,1	GT:PL:GQ	1/1:255,255,0:99
			chomp;
			my @l=split/\t/;
			($chr,$start,$stop,$rsid,$panel,$thresh1,$thresh2,$thresh3,$info,$chr2,$start2,$stop2,$ref,$alt,$qual,$filter,$info2,$format,$genotype)=@l;
			my @ref=($ref,split/,/,$alt);
			my($geno,$rest)=split/:/,$genotype,2;
			my @geno=map{$ref[$_]} split/\//,$geno;
			my $id=$rsid;
			$id=~s/^rs//;
			($dp4)=$info2=~/\bDP4=([\d,]+)\b/;
			my @dp=map{$_?$_:0} split/,/,$dp4;
			my $refC=$dp[0]+$dp[1];
			my $altC=$dp[2]+$dp[3];
			push @snps,[$id,"{rsid:'$rsid',ref:'$ref',alt:'$alt',geno1:'$geno[0]',geno2:'$geno[1]',panel:'$panel',depth:'$dp4',refCount:$refC,altCount:$altC}"];
		}
		close IN;
		$json.="{ _id: '$filename',\n  file: '$filename',\n  sample: '$sample',\n  type: '$type',\n  layout: '$layout',\n";
		$json.="  title: '$type markers for $filename',\n";
		$json.="  snpsArray: [\n";
		$json.=join(",\n",map{$_->[1]} sort{$a->[0]<=>$b->[0]} @snps)." ]\n}";
		$json{"$filename"}=$json;
}
print "[ ",join(",\n",values %json)," ]\n";

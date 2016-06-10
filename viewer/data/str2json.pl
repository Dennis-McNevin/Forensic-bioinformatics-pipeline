#!/usr/bin/env perl
use Data::Dumper;
use List::Util qw(sum);

my %primaryThresh=();
my %stutterThresh=();

open IN,"threshold.csv" or die "unable to open threshold.csv file in results directory";
while(<IN>) {
	chomp;
	my($locus,$type,$t,$s)=split/,/; #comma-delimited!
	$primaryThresh{$locus}=$t;
	$stutterThresh{$locus}=$s;
}
my %templAll=(
	'GlobalFiler'=>
		[['D3S1358','VWA','D16S539','CSF1PO','TPOX'],
		['Y Indel','Amelogenin','D8S1179','D21S11','D18S51','DYS391'],
		['D22S1045','S5S818','D13S317','D7S820','SE33'],
		['D2S441','D19S433','TH01','FGA'],
		['D10S1248','D1S1656','D12S391','D2S1338']],
	'PowerPlex Fusion'=>
		[['Amelogenin','D3S1358','D1S1656','D2S441','D19S1248','D13S317'],
		['D16S539','D18S51','D2S1338','CSF1PO','PentaD'],
		['D8S1179','D12S391','D19S433','FGA','D22S1045'],
		['TH01','VWA','D21S11','D7S820','D5S818','TPOX','DYS391'],
		[]],
	'PowerPlex 21'=>
		[['Amelogenin','D3S1358','D1S1656','D6S1043','D13S317','PentaE'],
		['D16S539','D18S51','D2S1338','CSF1PO','PentaD'],
		['D8S1179','D12S391','D19S433','FGA'],
		['TH01','VWA','D21S11','D7S820','D5S818','TPOX'],
		[]],
	'Qiagen HDplex'=>
		[['Amelogenin','D7S1517','D3S1744','D12S391','D2S1360','D6S474','D4S2366'],
		['D8S1132','D5S2500','D18S51','D21S2055'],
		[],
		['D10S2325','SE33'],
		[]],
	'Promega CS7'=>
		[['LPL','F13B','FES/FPS','F13A01','PentaD'],
		['PentaC'],
		[],
		['PentaE'],
		[]],
	'Qiagen Argus X12'=>
		[['Amelogenin','DXS10103','DXS8378','DXS7132','DXS10134'],
		['DXS10074','DXS10101','DXS10135'],
		['DXS7423','DXS10146','DXS10079'],
		['HPRTB','DXS10148'],
		[]],
	'Y-Filer 17'=>
		[['DYS456','DYS389I','DYS390','DYS389B.1'],
		['DYS458','DYS19','DYS385a/b'],
		['DYS393','DYS391','DYS439','DYS635','DYS392'],
		['GATA-H4','DYS437','DYS438','DYS448.1','DYS448.2',],
		[]],
	'Y-Filer Plus'=>
		[['DYS627','DYS389B.1','DYS635','DYS389I','DYS576'],
		['DYS391','DYS448.1','DYS448.2','GATA-H4','DYS19','DYS458','DYS460'],
		['DYS518','DYS392','DYS438','DYS390','DYS456'],
		['DYS449','DYS385a/b','DYS437','DYS570'],
		['DYS533','DYS387S1-ab','DYS481','DYS439','DYS393']],
	'PowerPlex Y-23'=>
		[['DYS576','DYS389I','DYS448.1','DYS448.2','DYS389B.1','DYS19'],
		['DYS391','DYS481','DYS549','DYS533','DYS438','DYS437'],
		['DYS570','DYS635','DYS390','DYS439','DYS392','DYS643'],
		['DYS393','DYS458','DYS385a/b','DYS456','GATA-H4'],
		[]]
);

my %dyeAll=(
	'codis'=>[qw/blue green red yellow purple cyan cyan cyan/],
	'ystr' =>[qw/blue green yellow red purple cyan cyan cyan/]
);

my %dyeMap=(
	'GlobalFiler'=>'codis',
	'PowerPlex Fusion'=>'codis',
	'PowerPlex 21'=>'codis',
	'Qiagen HDplex'=>'codis',
	'Promega CS7'=>'codis',
	'Qiagen Argus X12'=>'ystr',
	'Y-Filer 17'=>'ystr',
	'Y-Filer Plus'=>'ystr',
	'PowerPlex Y-23'=>'ystr'
);

my %json=();


for my $origname(@ARGV) {
	for my $layout(keys %templAll) {
		$json='';
		%a=();
		%ref=();
		@nums=();
		%unlisted=();
		%templ=();
		@templ=@{$templAll{$layout}};
		for my $dye(0..$#templ) {
			$templ{$_}=$dye for @{$templ[$dye]};
		}
#		print STDERR $layout,Dumper \%templ;
		$filename=$origname;
		$filename=~s/\.(codis|ystr)\.txt$/.\1/;
		my($sample,$type)=split/\./,$filename;
		@dyeMap=@{$dyeAll{$type}};
		open IN,$origname or die;
		while(<IN>) {
			chomp;
			my @l=split/\t/;
			if($#l>7) {
				($chr,$pos,$alleles,$major1,$major2,$unit,$ref,$locus,$allele1,$allele2)=@l;
				$type="CODIS";
			}else {
				($chr,$pos,$alleles,$offset,$unit,$ref,$locus,$allele1)=@l;
				$type="YSTR";
			}
			$ref{$locus}=$ref;
			my %al=();
			for my $al(split /;/,$alleles) {
				my($allele,$count)=split /\|/,$al;
				my $numAl=$ref+$allele/$unit;
				$al{$numAl}=$count;
				if(!defined $templ{$locus}) {
					$unlisted{$locus}++;
					$templ{$locus}=$#templ+1;
				}
				$nums[$templ{$locus}]{$numAl}++;
			}
			$a{$locus}=\%al;
		}
		close IN;
#		if($type eq "YSTR") {
#			@templ=();
#			my @loci=sort keys %unlisted;
#			push @templ,[splice @loci,0,6] while @loci;
#			for my $dye(0..5) {
#				for my $locus(@{$templ[$dye]}) {
#					$templ{$_}=$dye;
#					$nums[$dye]{$_}++ for keys %{$a{$locus}};
#				}
#			}
#		}else {
			my @loci=sort keys %unlisted;
#			print STDERR "unlisted: @loci\n";
			push @templ,[splice @loci,0,6] while @loci;
			for my $dye(0..7) {
				for my $locus(@{$templ[$dye]}) {
					if(defined $unlisted{$locus}) {
						$templ{$_}=$dye;
						$nums[$dye]{$_}++ for keys %{$a{$locus}};
					}
				}
			}
#			print STDERR Dumper(\@templ),"\n\n";
#		}
#		print STDERR $layout,Dumper \@templ;
		#open OUT,">$filename.json" or die;
		$json.="{ _id: '$filename|$layout',\n  file: '$filename',\n  sample: '$sample',\n  type: '$type',\n  layout: '$layout',\n";
		$json.="  title: '$type markers for $filename',\n";
		$json.="  categoriesArray: [\n";
		my @categories=();
		for my $dye(0..$#templ) {
			push @categories,"    [ ".join(", ",map{"'$_'"} @{$templ[$dye]})." ]"; 
		}
		my %aSum=();
		for my $l(keys %a) {
			$aSum{$l}=sum values %{$a{$l}};
		}
		$json.=join(",\n",@categories)."  ],\n";
		$json.="  seriesArray: [\n";
		my @series=();
		for my $dye(0..7) {
			my @loci=@{$templ[$dye]};
			my @n=sort{$a<=>$b} keys %{$nums[$dye]};
			my $series="    [";
			$series.="\t{ data: [".join(',',map{0} @loci).'] }' unless scalar @n;
			my @subseries=();
			for my $n(@n) {
				my $subseries="\t{ name: '$n', color: '".$dyeMap[$dye]."', data: [";
		        	$subseries.=join(",",map{defined $a{$_}{$n}?"{y:$a{$_}{$n},l:$n,p:".sprintf("%.2f",$a{$_}{$n}/$aSum{$_}*100).",pt:$primaryThresh{$_},st:$stutterThresh{$_},r:$ref{$_}}":0} @loci)."] }";
				push @subseries,$subseries;
			}
			$series.=join(",\n",@subseries)." ]";
			push @series,$series;
		}
		$json.=join(",\n",@series)." ]\n}";
		$json{"$filename|$layout"}=$json;
	}
}
print "[ ",join(",\n",values %json)," ]\n";
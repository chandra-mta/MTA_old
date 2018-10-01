#!/usr/bin/perl 

open(FH, "./zx_error_list");
@error_list = ();
while(<FH>){
	chomp $_;
	push(@error_list, $_);
}
close(FH);

open(FH, './telem.txt');
OUTER:
while(<FH>){
	chomp $_;
	if($_ =~ /AVG/ || $_ =~ /GRD/ || $_ =~ /GRAD/ || $_ =~ /PWR/ || $_ =~ /AWD/ || $_=~ /BIASLEAKI/ ){
	}else{
		foreach $comp (@error_list){
			if ($_ =~ /$comp/){
				next OUTER;
			}
		}
		print "$_\n";
	}
}
close(FH);

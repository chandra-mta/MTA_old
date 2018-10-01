#!/usr/bin/perl 
$file = $ARGV[0];
open(FH, "$file");
@list = ();
while(<FH>){
	chomp $_;
	if($_ =~ /ERROR/){
		@atemp = split(/\s+/, $_);
		push(@list, $atemp[4]);
		$prev  = $atemp[4];
	}elsif($_ =~ /New/ && $_ =~ /msid/){
		@atemp = split(/\s+/, $_);
		push(@list, $atemp[2]);
	}
}
close(FH);

@temp = sort(@list);
$prev = '';
foreach $ent (@list){
	if ($ent ne $prev){
		print "$ent\n";
		$prev = $ent;
	}
}



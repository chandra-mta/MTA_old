#!/usr/bin/perl 


open(FH, '/data/mta/Script/Weekly/Telem/clean_list');
open(OUT, '>/data/mta/Script/Weekly/Telem/reduced_clean_list');

while(<FH>){
    chomp $_;
    @atemp = split(/\s+/, $_);
    @btemp = split(//, $atemp[0]);
    if($btemp[0] eq 'A' || $btemp[0] eq 'C'){
        next;
    }elsif($atemp[0] =~ /TB1T/){
        next;
    }elsif($atemp[0] =~ /OHRT/){
        next;
    }elsif($atemp[0] =~ /OOB/){
        next;
    }elsif($atemp[0] =~ /4MP/){
        next;
    }elsif($atemp[0] =~ /4RT/){
        next;
    }else{
        if($btemp[-1] eq 'C'){
            next;
        }
        print OUT "$_\n";
    }
}

close(OUT);
close(FH);

#!/usr/bin/perl 

$input = `ls *.html`;
@list  = split(/\s+/, $input);

foreach $ent (@list){
    print "$ent\n";
    $line = `cat $ent`;
    #$line =~ s/.gif/.png/g;
    #$line =~ s/<html>/<!DOCTYPE html>\n<html>/g;
    #$line =~ s/a:link \{color:green\}//g;
    #$line =~ s/a:visited \{color:blue\}//s;
    #$line =~ s/<body style='color:black;background-color:white'>/<body style='color:#000000;background-color:#FFEBCD'>/g;
    #$line =~ s/background-color:white/background-color:#FFEBCD/g;
    $line =~ s/day of mission/year/g;



    open(OUT, ">$ent");
    print OUT  $line;
}

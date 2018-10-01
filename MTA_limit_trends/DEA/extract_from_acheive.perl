#!/usr/bin/perl 

for($year = 1999; $year < 2018; $year++){
    for($mon = 1; $mon < 13; $mon++){
        if($year == 1999 && $mon < 8){
            next;
        }elsif($year == 2017 && $mon > 10){
            last;
        }

        $cmon = $mon;
        if($mon < 10){
            $cmon = '0'."$mon";
        }
        $start = "$year".'-'."$cmon".'-01T00:00:00';

        if($mon == 12){
            $nyear = $year + 1;
            $stop = "$nyear".'-01-01T00:00:00';
        }else{
            $nmon = $mon + 1;
            $cnmon = $nmon;
            if($nmon < 10){
                $cnmon = '0'."$nmon";
            }
            $stop  = "$year".'-'."$cnmon".'-01T00:00:00';
        }

        print "$start <----> $stop\n";

        open(OUT, '>inline');
        print OUT "operation = retrieve\n";
        print OUT "dataset = flight\n";
        print OUT "detector = telem\n";
        print OUT "level = raw\n";
        print OUT "tstart = $start\n";
        print OUT "tstop  = $stop\n";
        print OUT "go\n";
        close(OUT);

        system("arc5gl -user isobe -script inline > zlist");

        system("rm -rf today_dump_files  input/*");

        open(FH, "zlist");
        open(OUT, ">today_dump_files");
        $chk = 0;
        while(<FH>){
            chomp $_;
            if($_ =~ /sto.gz/){
                system("mv $_ ./input");
                print OUT "$_\n";
                $chk++;
            }else{
                if($_ =~ /.gz/){
                    system("rm -f $_");
                }
            }
        }
        close(OUT);
        close(FH);
        system("rm -f inline zlist");

        print "$chk files extracted\n";

        system("prep.perl");
    }
}


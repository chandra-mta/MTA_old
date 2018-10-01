#!/usr/bin/perl 

#########################################################################################################
#                                                                                                       #
#       correct_rad_data_format.perl: correcting rad_data formt due to input data problem               #
#                                     check whether the data format is corrected or not before          #
#                                     using this, though it won't cause a problem                       #
#           author: t isobe (tisobe@cfa.harvard.edu)                                                    #
#                                                                                                       #
#           Last Update: Apr 28, 2014                                                                   #
#                                                                                                       #
#########################################################################################################

$file = $ARGV[0];
open(FH, $file);
while(<FH>){
    chomp $_;
    if($_ eq ''){
        next;
    }

    @atemp = split(/\s+/, $_);
    $cnt   = 0;
    foreach (@atemp){
        $cnt++;
    }
    if($cnt < 16){
        @btemp = split(//, $atemp[11]);
        $var1 = '';
        for($i = 0; $i< 8; $i++){
           $var1 = "$var1"."$btemp[$i]";
        }
        $var2 = '';
        for($i = 8; $i< 16; $i++){
           $var2 = "$var2"."$btemp[$i]";
        }

        $line = $atemp[0];
        for($i = 1; $i < 11; $i++){
            if($i < 3){
                $line = "$line "."$atemp[$i]";
            }elsif($i == 4){
                $line = "$line   "."$atemp[$i]";
            }elsif($i == 5){
                if($atemp[$i] < 100){
                    $line = "$line       "."$atemp[$i]";
                }elsif($atemp[$i] < 1000){
                    $line = "$line     "."$atemp[$i]";
                }elsif($atemp[$i] < 10000){
                    $line = "$line    "."$atemp[$i]";
                }else{
                    $line = "$line   "."$atemp[$i]";
                }
            }else{
                $line = "$line  "."$atemp[$i]";
            }
        }
        $line = "$line  "."$var1  "."$var2";
        for($i = 12; $i < 15; $i++){
            $line = "$line  "."$atemp[$i]";
        }
        $line = "$line\n";

        print "$line";
    } else{
        print "$_\n";
    }
}
close(FH);





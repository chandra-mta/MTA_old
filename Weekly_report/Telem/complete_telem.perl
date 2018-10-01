#!/usr/bin/perl 

system("perl telem.pl telem.txt telem.html -notab > zzz");
system("perl ./zx_find_error.perl zzz > zx_error_list");
system("perl ./zx_remove.perl > clean_list");
system("perl telem.pl clean_list telem.html  -notab");
system("rm -rf  zzz zx_error_list clean_list");

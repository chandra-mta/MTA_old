#!/usr/bin/perl

$org_file   = $ARGV[0];
$input      = $ARGV[1];
$tag        = $ARGV[2];

$org_text = `cat $org_file`;

$insert = `cat $input`;
$org_text =~s/$tag/$insert/;

print "$org_text";

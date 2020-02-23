# time_check.pl
# Read log(s) and generate times for loop, game, between games
#
use strict;
use warnings;

sub proc_file;
print "Args: @ARGV\n";
foreach my $file  (@ARGV) {
	proc_file($file)
}

sub proc_file {
	my ($filename) = @_;
	print "File: $filename\n";
	open(my $fh, '<:encoding(UTF-8)', $filename)
	  or die "Could not open file '$filename' $!";
	my $loop_no;
	my $ts_time;
	my $loop_begin_time;
	my $loop_begin_time_prev;
	my $end_game_time;
	my $end_game_time_prev;
	 
	while (my $line = <$fh>) {
	  chomp $line;
	  #print "$line\n";
	  if ($line =~ /^\s*(\d\d\d\d)(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d)/) {
	  	my $yr = $1;
	  	my $mth = $2;
	  	my $day = $3;
	  	my $hr = $4;
	  	my $min = $5;
	  	my $sec = $6;
	  	$ts_time = $sec + 60*$min + 60*60*$hr + 24*60*60*$day; ### forget mth,yr + 24*60*60*31*$mth
	  }
	  if ($line =~ /Loop\s+(\d+)/) {
	  	$loop_no = $1;
	  }
	  if ($line =~ /Memory Used:/) {
	  	if ($loop_begin_time) {
	  		$loop_begin_time_prev = $loop_begin_time;
	  	}
	  	$loop_begin_time = $ts_time;
	  }
	  if ($line =~ /end of game/) {
	  	$end_game_time = $ts_time;
	  	if ($end_game_time) {
	  		$end_game_time_prev = $end_game_time;
	  	}
	  	if ($end_game_time_prev && $loop_begin_time_prev) {
	  		my $game_len = $end_game_time - $loop_begin_time;
	  		my $loop_time = $loop_begin_time - $loop_begin_time_prev;
	  		printf("Loop %3d: Game time: %3d  Loop time: %3d\n",
	  			$loop_no, $game_len, $loop_time);
	  	}
	  }
	  
	}
	
}
<!DOCTYPE html>

<!--
    #################################################################################################
    #                                                                                               #
    #    msid_data_interactive.php                                                                  #
    #                                                                                               #
    #    This php script runs a python script to reate an interactive msid trend page.              #
    #    However, if it fails to create, it will dsiplay "the page is not created" notice           #
    #                                                                                               #
    #    author: t. isobe (tisobe@cfa.harvard.eud)                                                  #
    #                                                                                               #
    #    last update: Jan 31, 2018                                                                  #
    #                                                                                               #
    #################################################################################################
-->
<html>
<head>
    <title>MTA MSID Interactive Trending Page Creation</title>
</head>
<body style="width:95%;margin-left:10px; margin-right;10px;background-color:#FAEBD7;
font-family:Georgia, "Times New Roman", Times, serif">


<?php
    $msid    = $_POST['msid'];
    $group   = $_POST['group'];
    $ltype   = $_POST['ltype'];
    $mtype   = $_POST['mtype'];
    $tstart  = $_POST['tstart'];
    $tstop   = $_POST['tstop'];
    $binsize = $_POST['binsize'];
    
    /*
    echo 'MSID:   '.$msid.'<br />';
    echo 'Group:  '.$group.'<br />';
    echo 'Ltype:  '.$ltype.'<br />';
    echo 'Mtype:  '.$mtype.'<br />';
    echo 'START:  '.$tstart.'<br />';
    echo 'STOP:   '.$tstop.'<br />';
    echo 'BIN :   '.$binsize.'<br />';
    */
    

/* output file name */

    $out    = $msid.'_inter_avg.html';

/* run python script to crate the interactive page */

    exec("PYTHONPATH=/proj/sot/ska/arch/x86_64-linux_CentOS-5/lib/python2.7/site-packages  /proj/sot/ska/bin/python   /data/mta/Script/MTA_limit_trends/Scripts/create_interactive_page.py $msid $group $tstart $tstop $binsize ");

/* check wether the page actually created */

    if(file_exists($out) == 1){

    echo '<h2>Interactive Trending Page Is Created!</h2>';
    $wpage = 'http://cxc.cfa.harvard.edu/mta/www/MSID_Trends/Interactive/'.$msid.'_inter_avg.html';

    echo '<h3>Please Open: ';
    echo '<a href=" '.$wpage.'" target=blank>'.$msid.'</a> (the page will open on a new tab).</h3>';

    echo '<div style="font-size:90%;">';
    echo '<ul>';
    echo '<li>Note 1: It may take a while to load the interactive page.</li>';
    echo '<li>Note 2: The page will be kept under:';
    echo '<br /><br /><em>'.$wpage.'</em>';
    echo '<br /><br /> for a day and then deleted.</li>';
    echo '</ul>';

    }else{

/* if the page is not created, display the "not created" notice */

    echo '<title>Page Not Created Notice</title>';
    echo '</head>';
    echo '<body style="width:95%;margin-left:10px; margin-right;10px;background-color:#FAEBD7;font-family:Georgia, "Times New Roman", Times, serif">';

    echo '<h2 style="padding-top:30px;">Sorry! The Page Was Not Created!</h2>';
    echo '<p>';
    echo 'The requested interactive page was not created. There are a few possible reasons.';
    echo '</p>';

    echo '<ol>';
    echo '    <li> The requested data are too large and the system could not handle.';
    echo '        <ul>';
    echo '            <li>You can try again; it could be the cpu is less taxed when the time you try again.</li>';
    echo '            <li>Reduce the time span and/or the sample size.</li>';
    echo '        </ul>';
    echo '    </li>';
    echo '    <li style="padding-top:20px"> There were no data in the requested period.';
    echo '        <ul>';
    echo '            <li>Although this is a less likely case, you can try to see whether the different period';
    echo '                will create the plot. If it does, please report to';
    echo '                <a href="mailto:tisobe@cfa.harvard.edu">tisobe@cfa.harvard.edu</a>.';
    echo '            </li>';
    echo '        </ul>';
    echo '    </li>';
    echo '    <li style="padding-top:20px"> The data are not in the SOT engineering database.';
    echo '        <ul>';
    echo '            <li>The interactive plot can be produced only when the data are in SOT engineering';
    echo '            database. This is the major causes of not producing the interactive plot.';
    echo '            </li>';
    echo '            <li>';
    echo '            A msid with condtions (such as HRC with HRC-I is in use) are not in the database';
    echo '            and computed data (such as HRMA computed average) are not in the database.';
    echo '            </li>';
    echo '        </ul>';

    echo '    </li>';

    echo '</ol>';
}

/* change the permission so that non-"http" user can delete the file */

    exec('chmod 777 /data/mta4/www/MSID_Trends/Interactive/*html ');

    $back_page = 'https://cxc.cfa.harvard.edu/mta/MSID_Trends/';
    $umsid = ucfirst($msid);
    $back_page = $back_page.$group.'/'.$umsid.'/'.$msid.'_'.$mtype.'_static_'.$ltype.'_plot.html';
    echo  '<p style="padding-top:30px;"><a href="'.$back_page.'"><b>Return to '.$msid.' page.</b></a></p>';
?>


<div style='padding-top:300px'>
</div>

<hr />
<p style="text-align:left; padding-top:10px;padding-bottom:20px">
If you have any questions, please contact
<a href="mailto:tisobe@cfa.harvard.edu">tisobe@cfa.harvard.edu</a>.



</body>
</html>

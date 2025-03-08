#! /bin/bash
clear
home/sysadm
HOST='hostname'
OS='uname'
DATE='date +%y%m%d'
DATE_TIME='date +%y%m%d%H:%M:%S'

echo "To Continue, press Enter key .....\c"
echo "\n"
read continue

function display_main_menu
{
    clear
    echo " "
    echo " "
    echo " *****************************************************************"
    echo " **                                                             **"
    echo " **           hostname : $HOST                                  **"
    echo " **                                                             **"
    echo " *****************************************************************"
    echo "*                                                                *"
    echo "*  1) Server check script set                                    *"
    echo "*     (Just use when server is modified!!)                       *"
    echo "*                                                                *"
    echo "*  2) Server check                                               *"
    echo "*                                                                *"
    echo "*  3) Show detail server logs                                    *"
    echo "*                                                                *"
    echo "*  4) Show server performance                                    *"
    echo "*                                                                *"
    echo "*  5) Show log messages                                          *"
    echo "*                                                                *"
    echo "*  q) Quit                                                       *"
    echo "*                                                                *"
    echo " *****************************************************************"
    echo " "
    echo "   Select the Nunber of your job : \c"
    read MAIN_MENU
    return $MAIN_MENU
}

function performance
{
    clear
echo ""
echo "---------------------------------------"
echo  "SAR Info....\n"
echo "---------------------------------------"
sar 2 5
echo ""

echo "---------------------------------------"
echo  "Extracting VMSTAT info...\n"
echo "---------------------------------------"
vmstat 2 5
echo ""

echo "---------------------------------------"
echo  "Extracting memory usage info...\n"
echo "---------------------------------------"
memory
echo ""
    echo "    ***************************************************************"
    echo "    Finished perf checking....Press Enter key........!!!!!!!"
    echo "    ***************************************************************"
            read continue
}

function show_server_detail_log {
    countnum=0
    export countnum

    countnumd() {
        countnum=$((countnum + 1))
        echo "* [ $countnum ] $1 "
    }

    clear 
    while true
    do
        echo "   *************************************************************"
        countnum=0
        export countnum

        > /tmp/count.txt  # 기존 파일 초기화

        while read i; do
            countnumd "$i" >> /tmp/count.txt
        done < /home/sysadm/emergency/tmp_server.txt

        echo "" >> /tmp/count.txt
        echo "  --> [ 50 ] Quit!!!!!!!!" >> /tmp/count.txt
        echo "" >> /tmp/count.txt
        cat /tmp/count.txt
        echo "  **************************************************************"
        echo ""
        echo -n "    Select the Number of your job : "
        read MENU1

        if [ $MENU1 -le 40 ] ; then
            para=$(grep " $MENU1 ]" /tmp/count.txt | awk '{print $5}')

            echo "-----------------------------"
            echo "$para detail list"
            echo "-----------------------------"
            echo " original setting list       "
            echo "-----------------------------"
            cat /home/sysadm/emergency/ORG_SERVER/$para

            echo "-----------------------------"
            echo " current setting list        "
            echo "-----------------------------"
            cat /home/sysadm/emergency/$DATE/$para

            echo "To continue, press Enter Key ......."
            read Continue
            rm /tmp/count.txt
            clear 
        else
            clear
            rm /tmp/count.txt
            echo " There is no more process"
            break
        fi
    done
}


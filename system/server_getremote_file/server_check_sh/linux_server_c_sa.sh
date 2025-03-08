#! /bin/bash

LANG=en_US.UTF-8

HOST='hostname'
OS='uname'
DATE='date +%y%m%d'
DATE_TIME='date +%y%m%d%H:%M:%S'
YESTERDAY='date -d yesterday +%y%m%d'

# file diff 
STD_FILE1="ls -l /home/sysadm/emergency | awk "{print $9}" | grep "${HOST}_" | sort | tail -1"
STD_FILE="ls -l /home/sysadm/emergency/${STD_FILE1}/"

NOW_FILE="ls -l /home/sysadm/emergency | awk "{print $9}" | grep "${HOST}_" | sort | tail -1 | cut -d _ -f 2"

#raw data 
MK_DIR="/home/sysadm/emergency/${HOST}_${DATE_TIME}/"
echo $MK_DIR
mkdir $MK_DIR

#     : >> $MK_DIR"${HOST}_report_"$DATE
echo $HOST >> $MK_DIR"${HOST}_report_"$DATE

# 01 - 02 cpu 
# 01. cpu mpstat
mpstat 1 10 >> $MK_DIR"cpu_mpstat_"$DATE

# 02.cpu sar
 # cpu sar yesterday
sa00='date -d yesterday +%d'
sar -u -f /var/log/sa/sa${sa00} >> $MK_DIR"cpu_sar_"$DATE
# cpu sar now 
sar >> $MK_DIR"cpu_sar_"$DATE

# cpu sar max (1 day max)
max_hap=0

for i in 1 2 3 4 5 6 7 
do  
    DAY='date +%d -d "-${i} days"'
    max="sar -u -f /var/log/sa/sa$DAY | sort -k 8 | head -5 | tail -1 | awk '{svg=100-$NF}{print svg}'"
    max_hap=$(echo "scale=2; $MAX_hap + $max" | bc )
done

avg1=$(echo "scale=2; $max_hap / 7" | bc )

# now cpu
now1="sar 1 10 | grep Average | awk '{svg=100-$NF}{print svg}'"

printf "01 cpu_used: %.2f %%   \n" $now1 >> $MK_DIR"${HOST}_report_"$DATE
printf "02 cpu_max_used_avg: %.2f %%  " $avg1 >> $MK_DIR"${HOST}_report_"$DATE
printf "\n"  >> $MK_DIR"${HOST}_report_"$DATE

# 03. 04 Memory 
# memory stat 
printf "# memory \n" >> $MK_DIR"memory_"$DATE
memory >> $MK_DIR"memory_"$DATE
printf "\n # cat /proc/memeinfo \n" >> $MK_DIR"memory_"$DATE
cat /proc/memeinfo \n >> $MK_DIR"memory_"$DATE 

MEM_used='memory | grep "memory usage is" | awk '{print $4}''

if [ $(echo "scale=1; $MEM_used <= 80" |bc) -ne 0 ]; then
    printf "03 memory_usage GOOD__%.2f %% \n" $MEM_used >> $MK_DIR"${HOST}_report_"$DATE
else 
    printf "03 memory_usage_is_high memory_high_%.2f %% \n" $MEM_used >> $MK_DIR"${HOST}_report_"$DATE
fi

# memory change 
y_price="cat $STD_FILE"memory_"$NOW_FILE | grep 'memory usage is' | awk '{print $4}'"

amount_of_change=$( echo "$y_price; $MEM_used" | awk '{printf "%f", $1 - $2}' )
printf "04 amount_of_change: %.2f %%" $amount_of_change >> $MK_DIR"${HOST}_report_"$DATE
printf "\n"  >> $MK_DIR"${HOST}_report_"$DATE

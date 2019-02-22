#!/bin/bash

export DISPLAY=:0
xset -dpms
xset s noblank
xset s off

unclutter -idle 0.5 -root &

sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/pi/.config/chromium/Default/Preferences
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/pi/.config/chromium/Default/Preferences

/usr/bin/chromium-browser --noerrdialogs --disable-infobars --kiosk \
	https://events.fixme.ch/ \
	'https://www.t-l.ch/tl-live-mobile/line_detail.php?from=horaire&id=3377704015497514&line=11821953316814853&id_stop=2533279085551134&id_direction=11821953316814853&lineName=17' &

while true; do
	xdotool keydown ctrl+Tab; xdotool keyup ctrl+Tab;
	sleep 30
done


# Remove leftover Xvfb lock files
rm -f /tmp/.X*-lock
# Reason for "-nolisten tcp", not documented within Xvfb manpages (for who knows what reason)
# https://superuser.com/questions/855019/make-xvfb-listen-only-on-local-ip
Xvfb :99 -screen 0 1280x1024x8 -nolisten tcp &
# Keeps docker container alive so you can attach a shell
/bin/bash ./keep-alive.sh node-bot-dev
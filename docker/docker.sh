#!/bin/bash -xe

cat >/usr/share/dbus-1/services/org.freedesktop.Notifications.service <<EOF
[D-BUS Service]
Name=org.freedesktop.Notifications
Exec=/usr/lib/notification-daemon/notification-daemon
EOF

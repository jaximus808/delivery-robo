#!/usr/bin/env bash
# Sets up WiFi on the robot Pi: try the hotspot first, fall back to wustl-guest.
# Run ON THE PI:  HOTSPOT_SSID='my phone' HOTSPOT_PSK='secret' sudo -E deployment/wifi/install.sh
#
# Uses wpa_supplicant@wlan0 (priority-ordered SSIDs) + systemd-networkd DHCP,
# which is the stock Ubuntu Server stack. Existing netplan WiFi config is moved
# aside so the two don't fight over wlan0.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
IFACE="${IFACE:-wlan0}"
: "${HOTSPOT_SSID:?set HOTSPOT_SSID}"
: "${HOTSPOT_PSK:?set HOTSPOT_PSK}"
[ "$(id -u)" = 0 ] || { echo "run with sudo -E"; exit 1; }

# wpa_supplicant config with the secrets filled in
sed -e "s|__HOTSPOT_SSID__|$HOTSPOT_SSID|" -e "s|__HOTSPOT_PSK__|$HOTSPOT_PSK|" \
  "$HERE/wpa_supplicant-wlan0.conf" > "/etc/wpa_supplicant/wpa_supplicant-$IFACE.conf"
chmod 600 "/etc/wpa_supplicant/wpa_supplicant-$IFACE.conf"

# DHCP on the wifi interface via systemd-networkd
cat > "/etc/systemd/network/25-$IFACE.network" <<NET
[Match]
Name=$IFACE
[Network]
DHCP=yes
[DHCPv4]
RouteMetric=600
NET

# Park any netplan wifi definitions so netplan stops managing wlan0 (the Pi
# had a cloud-init networkd one and a stale NetworkManager one).
mkdir -p /etc/netplan/disabled
for f in /etc/netplan/*.yaml; do
  grep -q "wifis:" "$f" 2>/dev/null && mv "$f" /etc/netplan/disabled/ && echo "moved $f aside"
done
rm -f /etc/netplan/*.yaml~
# keep cloud-init from writing a fresh netplan wifi config on a later boot
echo 'network: {config: disabled}' > /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
netplan generate || true
systemctl stop "netplan-wpa-$IFACE.service" 2>/dev/null || true

systemctl enable --now systemd-networkd
systemctl disable --now wpa_supplicant.service 2>/dev/null || true
systemctl enable --now "wpa_supplicant@$IFACE"
systemctl restart "wpa_supplicant@$IFACE" systemd-networkd
echo "done. check: wpa_cli -i $IFACE status | grep -E 'ssid|state'; networkctl status $IFACE"

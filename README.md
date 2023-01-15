# StreamX Purchasing Backend

### Installation

To fetch the latest dev build, fetch directly from Github:
```sh
git clone https://github.com/Roblox-StreamX/Purchase
cd Purchase
python3 -m pip install -r requirements.txt
```

Alternatively, download the latest binary from [Github Releases](https://github.com/Roblox-StreamX/Payment/releases):
```sh
wget https://github.com/Roblox-StreamX/Payment/releases/latest/download/paymentserver
```

---

You can now either run the server manually by executing `python3 bootstrap.py` (or `paymentserver`).  
If preferred, you can setup a systemd config file:
```
# /lib/systemd/system/streamx-payment.service
[Unit]
Description=StreamX Payment Server
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=python3 /path/to/bootstrap.py

# If using a compiled binary:
#ExecStart=/path/to/paymentserver

[Install]
WantedBy=multi-user.target
```
Then you can simply:
```sh
sudo systemctl daemon-reload
sudo systemctl enable streamx-payment
sudo systemctl start streamx-payment
```

### Configuration via STREAMX_UPSTREAM

To ease configuration in multi-server setups, StreamX has a `STREAMX_UPSTREAM` environment variable which can set either to the IP and port
of a [StreamX Configuration Server](https://github.com/Roblox-StreamX/Configuration) or set to `file` to load a local `config.json` file inside the StreamX folder.

To see the `config.json` format, please see [StreamX Configuration Server](https://github.com/Roblox-StreamX/Configuration).

# Wi‑Fi Coverage and SSID Mapping

```mermaid
graph LR
  Floor1[Main Floor]
  Floor2[Second Floor]
  Yard[Patio/Yard]

  AP1[U6-LR SSIDs: Trusted/IoT/Guest]
  AP2[U6-Lite SSIDs: Trusted/IoT/Guest]

  AP1 --> Floor1
  AP1 --> Yard
  AP2 --> Floor2

  style AP1 fill:#7fb3ff,stroke:#1a62d8
  style AP2 fill:#7fb3ff,stroke:#1a62d8
  style Floor1 fill:#e8f5e9,stroke:#2e7d32
  style Floor2 fill:#e8f5e9,stroke:#2e7d32
  style Yard fill:#e8f5e9,stroke:#2e7d32
```

- **Roaming**: 20 MHz channels on 2.4 GHz, 80 MHz on 5 GHz; minimum RSSI -70 dBm enforced for band steering.
- **Guest**: Captive portal on VLAN 40; rate limited to 10 Mbps down/2 Mbps up.
- **IoT**: Client isolation enabled; multicast enhancement for smart-home devices.

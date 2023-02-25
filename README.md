<h2 align="center"> <b>C</b>OM port <b>T</b>o <b>S</b>ocket (CTS) server</h2>

<h3 align="left">
Simple Serial Port to Socket converter server driven by <b>asyncio</b> and <b>serial_asyncio</b>.</h3>

<b><h3>Usage:</h3></b>
 - python CTS_server.py --serial COM5 --speed 230400 --host localhost --port 8888


<b><h3>Server can handle 3 types of clients:</h3></b>

- Modbus TCP client (default)
- RAW data clients
- Listener client

<b><h3>Command List:</h3></b>
 - 'close'   - shutdown server
- 'version' - server version
- 'info'    - get serial name adn speed 
- 'type modbus' - modbus TCP client
- 'type raw' - raw client
- 'type listener' - listener client

Use CTS_launcher.py for simple start GUI




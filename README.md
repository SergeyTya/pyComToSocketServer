<h2 align="center"> <b>C</b>OM port <b>T</b>o <b>S</b>ocket (CTS) server</h2>

<h3 align="left">
Simple Serial Port to Socket converter server driven by <b>asyncio</b> and <b>serial_asyncio</b>.</h3>

<b><h3>Usage:</h3></b>
 - python CTS_server.py --serial COM5 --speed 230400 --host localhost --port 8888


<b><h3>Server can handle 3 types of clients:</h3></b>

- Modbus TCP client (default)
- RAW data clients
- Listener client

To setup client type send "type raw" or "type modbus" or "type listener" to server after or during connection 




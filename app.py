import asyncio
import json
import serial
import serial.tools.list_ports
import threading
import time
from aiohttp import web, WSMsgType
import pathlib

# 参数映射
BYTESIZE_MAP = {
    5: serial.FIVEBITS,
    6: serial.SIXBITS,
    7: serial.SEVENBITS,
    8: serial.EIGHTBITS
}

PARITY_MAP = {
    'None': serial.PARITY_NONE,
    'Even': serial.PARITY_EVEN,
    'Odd': serial.PARITY_ODD,
    'Mark': serial.PARITY_MARK,
    'Space': serial.PARITY_SPACE
}

STOPBITS_MAP = {
    1: serial.STOPBITS_ONE,
    1.5: serial.STOPBITS_ONE_POINT_FIVE,
    2: serial.STOPBITS_TWO
}

class SerialManager:
    def __init__(self):
        self.ser = None
        self.is_simulated = False
        self.rx_thread = None
        self.running = False
        self.loop = None
        self.ws_clients = set()
        self.is_hex_mode = False
        self.rx_encoding = "utf-8"
        self.last_ports = []
        # 启动端口扫描线程
        self.scan_thread = threading.Thread(target=self._scan_ports_loop, daemon=True)
        self.scan_thread.start()

    def get_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        return ["SIMULATOR"] + ports

    def _scan_ports_loop(self):
        while True:
            try:
                current_ports = self.get_ports()
                if current_ports != self.last_ports:
                    self.last_ports = current_ports
                    if self.loop and self.ws_clients:
                        asyncio.run_coroutine_threadsafe(
                            self.broadcast({"type": "ports", "data": current_ports}), 
                            self.loop
                        )
            except Exception as e:
                print(f"Port scan error: {e}")
            time.sleep(1)

    def connect(self, port, baudrate, bytesize=8, parity='None', stopbits=1, flow_control='None'):
        self.disconnect()
        if port == "SIMULATOR":
            self.is_simulated = True
            self.running = True
            return True, "模拟模式已启动"
        try:
            # 参数转换
            bs = BYTESIZE_MAP.get(int(bytesize), serial.EIGHTBITS)
            par = PARITY_MAP.get(parity, serial.PARITY_NONE)
            sb = STOPBITS_MAP.get(float(stopbits), serial.STOPBITS_ONE)
            
            xonxoff = False
            rtscts = False
            
            if flow_control == 'XON/XOFF':
                xonxoff = True
            elif flow_control == 'RTS/CTS':
                rtscts = True

            self.ser = serial.Serial(
                port, 
                baudrate, 
                bytesize=bs,
                parity=par,
                stopbits=sb,
                xonxoff=xonxoff,
                rtscts=rtscts,
                timeout=0.1
            )
            self.is_simulated = False
            self.running = True
            self.rx_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.rx_thread.start()
            return True, f"已连接到 {port}"
        except Exception as e:
            return False, str(e)

    def disconnect(self):
        self.running = False
        self.is_simulated = False
        if self.ser and self.ser.is_open:
            try:
                self.ser.reset_input_buffer()
            except Exception:
                pass
            try:
                self.ser.reset_output_buffer()
            except Exception:
                pass
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None
        if self.rx_thread and self.rx_thread.is_alive():
            self.rx_thread.join(timeout=0.5)
        self.rx_thread = None

    def send_data(self, data: bytes, delay=0.002):
        if self.is_simulated:
            # 模拟回显
            asyncio.run_coroutine_threadsafe(self.broadcast({"type": "rx", "data": f"[SIM] Echo: {data.hex(' ')}"}), self.loop)
            return
        
        if self.ser and self.ser.is_open:
            def _task():
                for b in data:
                    if not self.running or not self.ser or not self.ser.is_open:
                        break
                    self.ser.write(bytes([b]))
                    time.sleep(delay) # 逐帧/字节发送
                if self.ser and self.ser.is_open:
                    self.ser.flush()
            threading.Thread(target=_task).start()

    def _read_loop(self):
        while self.running and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    data = self.ser.read(1024)
                    if data and self.loop:
                        # 将接收到的数据推送到所有WS客户端
                        if self.is_hex_mode:
                            payload = {"type": "rx", "data": data.hex(' ')}
                        else:
                            payload = {"type": "rx", "data": data.decode(self.rx_encoding, errors='replace')}
                        asyncio.run_coroutine_threadsafe(self.broadcast(payload), self.loop)
            except:
                break
            time.sleep(0.01)

    async def broadcast(self, message):
        for ws in self.ws_clients:
            await ws.send_json(message)

manager = SerialManager()

# ============= 路由处理 =============
async def index(request):
    return web.FileResponse(pathlib.Path(__file__).parent / "index.html")

async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    manager.ws_clients.add(ws)
    manager.loop = asyncio.get_running_loop()
    
    # 初始化时发送串口列表
    await ws.send_json({"type": "ports", "data": manager.get_ports()})

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                req = json.loads(msg.data)
                cmd = req.get("cmd")
                
                if cmd == "connect":
                    success, info = manager.connect(
                        req['port'], 
                        req['baud'],
                        req.get('bytesize', 8),
                        req.get('parity', 'None'),
                        req.get('stopbits', 1),
                        req.get('flow_control', 'None')
                    )
                    await ws.send_json({"type": "status", "success": success, "connected": bool(success), "msg": info})

                elif cmd == "disconnect":
                    manager.disconnect()
                    await ws.send_json({"type": "status", "success": True, "connected": False, "msg": "已断开连接"})
                
                elif cmd == "update_config":
                    if 'isHexShow' in req:
                        manager.is_hex_mode = req['isHexShow']
                    if 'rxEncoding' in req:
                        manager.rx_encoding = str(req['rxEncoding'] or "utf-8")

                elif cmd == "send":
                    raw_data = req['data']
                    is_hex = req.get('isHex', False)
                    try:
                        if is_hex:
                            # 过滤非 HEX 字符
                            import re
                            hex_str = re.sub(r'[^0-9a-fA-F]', '', raw_data)
                            if len(hex_str) % 2 != 0:
                                hex_str += '0'  # 补齐最后一位
                            send_bytes = bytes.fromhex(hex_str)
                        else:
                            send_bytes = raw_data.encode()
                        manager.send_data(send_bytes)
                    except Exception as e:
                        await ws.send_json({"type": "error", "msg": f"发送失败: {e}"})

    finally:
        manager.ws_clients.remove(ws)
    return ws

app = web.Application()
app.router.add_get('/', index)
app.router.add_get('/ws', ws_handler)

if __name__ == "__main__":
    web.run_app(app, port=5678)

import { ControllerApiService } from "./controller-api.service"

class Ws {
    public readyState = WebSocket.OPEN
    public orig_handler: any;

    public send(data: any) {
        console.log("[WS-MSG]", data)

        //patch

        setTimeout(() => {
            try {
                const d = JSON.parse(data);
                switch (d.type) {
                    case "select_drone":
                        this.mock_recv(JSON.stringify({
                            type: "drone_connected",
                            rtc_sdp: "mock",
                            rtc_type: "mock",
                        }))
                        break;
                    
                    case "record_stop":
                        this.mock_recv(JSON.stringify({
                            "type": "recording_name",
                            "name": "gibtsned.mp4"
                        }))
                        break;
                
                    default:
                        break;
                }
            } catch (error) {
                console.error("error in mock", error)
            }

        }, 100);
    }

    public mock_recv(data: string) {
        console.log("[WS-MOCK]", data)
        this.orig_handler({data})
    }
}

export const patch = (inst: ControllerApiService) => {
    // @ts-ignore
    window.controllerApi = inst

    const ws = new Ws();

    // @ts-ignore
    ws.orig_handler = (e) => inst.handle_message.call(inst, e);
    // @ts-ignore
    inst.ws = ws;

    setTimeout(() => {
        inst.status.set("ws_connected")
    }, 100);
}
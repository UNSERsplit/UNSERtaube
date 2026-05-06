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
                        }))
                        break;
                    
                    case "replay_recording":
                        this.mock_recv(JSON.stringify({
                            type: "accepted",
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

    inst.get_drones = async () => {
        return [
            {
                id: "f49d3a01-0797-489e-8181-73c13cbf10ee",
                name: "Drone 1",
                ip: "1.1.1.1"
            },
            {
                id: "81437596-326c-49fe-82ad-b38f483e3265",
                name: "Drone 2",
                ip: "2.2.2.2"
            },
            {
                id: "3af9fb46-46fc-439a-8040-bc262ef0d4cd",
                name: "Drone 3",
                ip: "3.3.3.3"
            }
        ]
    }

    inst.get_paths = async () => {
        return [{
                id: "f49d3a01-0797-489e-8181-73c13cbf10ee",
                drone_id: "f49d3a01-0797-489e-8181-73c13cbf10ee",
                drone_name: "Drone 1",
                name: "Drone 1",
                ip: "1.1.1.1",
                duration: 10,
                distance: 100
            },
            {
                id: "81437596-326c-49fe-82ad-b38f483e3265",
                drone_id: "81437596-326c-49fe-82ad-b38f483e3265",
                drone_name: "Drone 2",
                name: "Drone 2",
                ip: "2.2.2.2",
                duration: 20,
                distance: 200
            },
            {
                id: "3af9fb46-46fc-439a-8040-bc262ef0d4cd",
                drone_id: "3af9fb46-46fc-439a-8040-bc262ef0d4cd",
                drone_name: "Drone 3",
                name: "Drone 3",
                ip: "3.3.3.3",
                duration: 30,
                distance: 300
            }
        ]
    }

    setTimeout(() => {
        inst.status.set("ws_connected")
    }, 100);
}
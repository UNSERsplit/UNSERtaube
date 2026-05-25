import { ControllerApiService } from "./controller-api.service"

class Ws {
    public readyState = WebSocket.OPEN
    public orig_handler: any;

    public send(data: any) {
        console.log("[WS-MSG]", data)

        //patch

        
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

    inst.action = async (method: string, url: string, body: any) => {
        if (method == "GET" && url == "drone") {
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

        if (method == "GET" && url == "recording") {
            return [
                {
                    id: "f49d3a01-0797-489e-8181-73c13cbf10ee",
                    drone: {
                        id: "f49d3a01-0797-489e-8181-73c13cbf10ee",
                        name: "Drone 1",
                        ip: "1.1.1.1"
                    },
                    name: "Flug 1",
                    duration: 10,
                    distance: 100
                },
                {
                    id: "81437596-326c-49fe-82ad-b38f483e3265",
                    drone: {
                        id: "f49d3a01-0797-489e-8181-73c13cbf10ee",
                        name: "Drone 1",
                        ip: "1.1.1.1"
                    },
                    name: "Flug 2",
                    duration: 20,
                    distance: 200
                },
                {
                    id: "3af9fb46-46fc-439a-8040-bc262ef0d4cd",
                    drone: {
                        id: "3af9fb46-46fc-439a-8040-bc262ef0d4cd",
                        name: "Drone 3",
                        ip: "3.3.3.3"
                    },
                    name: "Flug 3",
                    duration: 30,
                    distance: 300
                }
            ]
        }

        if (method == "GET" && url == "live/connected") {
            return {
                        id: "3af9fb46-46fc-439a-8040-bc262ef0d4cd",
                        name: "Drone 3",
                        ip: "3.3.3.3"
                    }
        }

        if (method == "GET" && url == "live/matrix/pattern") {
            return "rpbrpbrpbrpbrpb0000000000000000000000000000000000000000000000000"
        }

        if (method == "POST" && url == "drone/") {
            return {
                    id: "f49d3a01-0797-489e-8181-73c13cbf10ee",
                    name: "Drone 1",
                    ip: "1.1.1.1"
                }
        }

        return "ok"
    }

    inst.start = (callback) => {
        setTimeout(() => {
            inst.status.set("ws_connected");

            callback({
                connected: true,
                
            })
        }, 100);
    }
}
export class Drone {
    private _name: string;
    private _ip: string;
    private _id: string;

    constructor(name: string, ip: string, id: string) {
        this._name = name;
        this._ip = ip;
        this._id = id;
    }

    get getName(): string {return this._name}
    get getIp(): string { return this._ip; }
    get getId(): string { return this._id; }
}




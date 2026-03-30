export class Drone {
    private _name: string;
    private _ip: string;

    constructor(name: string, ip: string) {
        this._name = name;
        this._ip = ip;
    }

    get getName(): string {return this._name}
    get getIp(): string { return this._ip; }
}




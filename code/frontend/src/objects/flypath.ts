export class flypath{
    private _flugName: string;
    private _name: string;
    private _ip: string;
    private _flugZeit: string;
    private _flugDistanz: string;


    constructor(flugName: string, name: string, ip: string, flugZeit: string, flugDistanz: string) {
        this._flugName = flugName;
        this._name = name;
        this._ip = ip;
        this._flugZeit = flugZeit;
        this._flugDistanz = flugDistanz;
    }

    get flugName(): string {
        return this._flugName;
    }

    get name(): string {
        return this._name;
    }

    get ip(): string {
        return this._ip;
    }

    get flugZeit(): string {
        return this._flugZeit;
    }

    get flugDistanz(): string {
        return this._flugDistanz;
    }
}

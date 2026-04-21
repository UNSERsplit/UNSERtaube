export class flypath{
    private _flugName: string;
    private _name: string;
    private _ip: string;
    private _flugZeit: string;
    private _flugDistanz: string;
    private _id: string


    constructor(flugName: string, name: string, ip: string, flugZeit: string, flugDistanz: string, id: string) {
        this._flugName = flugName;
        this._name = name;
        this._ip = ip;
        this._flugZeit = flugZeit;
        this._flugDistanz = flugDistanz;
        this._id = id;
    }

    get flugName(): string {
        return this._flugName;
    }

    get id(): string {
        return this._id;
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

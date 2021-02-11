'use strict';

const { Pool, Client } = require('pg');
const config = require('config');

class Db {
	constructor() {
		this.connection = new Pool(config.get("pool"));
	}
	query(sql, args) {
		return new Promise((resolve, reject) => {
			this.connection.query(sql, args, (err, rows) => {
				if (err){
					return reject(err);
                }
				resolve(rows);
			});
		});
	}
	close() {
		return new Promise((resolve, reject) => {
			this.connection.end(err => {
				if (err)
					return reject(err);
				resolve();
			});
		});
	}
}
module.exports = new Db();

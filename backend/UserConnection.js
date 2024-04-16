const Pool = require('pg').Pool

// Note: utting credentials is not recommended. 
// Change to .env file further on.
const pool = new Pool({
  user: 'postgres',
  host: '147.83.46.71',
  database: 'usersDB', // eulaliadb
  password: 'password',
  port: 5990,
});

// Create a new user record in the databsse
const createUser = (body) => {
    return new Promise(function (resolve, reject) {
      const {id, username, password } = body;
      pool.query(
        // Taula: users_login
        "INSERT INTO users_login (id, username, password) VALUES ($1, $2, $3) RETURNING *",
        [id, username, password],
        (error, results) => {
          if (error) {
            reject(error);
          }
          if (results && results.rows) {
            resolve(
              `A new merchant has been added: ${JSON.stringify(results.rows[0])}`
            );
          } else {
            reject(new Error("No results found"));
          }
        }
      );
    });
  };

  module.exports = {
    createUser
  };
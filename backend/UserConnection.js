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

// Create a new user record in the database
const createUser = (body) => {
  return new Promise(function (resolve, reject) {
    const { username, password } = body;
    pool.query(
      "INSERT INTO users_login (username, password) VALUES ($1, $2) RETURNING *",
      [username, password],
      (error, results) => {
        if (error) {
          reject(error);
        }
        if (results && results.rows) {
          resolve(
            `A new user has been added: ${JSON.stringify(results.rows[0])}`
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
const { Pool } = require('pg');

const pool = new Pool({
  user: 'postgres',
  host: '147.83.46.71',
  password: 'password',
  database: 'usersDB', // eulaliadb
  port: 5990,
});


pool.query('SELECT * FROM users_login;').then((res) => {
  console.log('Data');
  console.log(res.rows);
  pool.end();
})
.catch((err) => {
  console.log('Error');
  console.log(err);
  pool.end();
});

module.exports = pool;

// // Create a new user record in the databsse
// const createUser = (body) => {
//     return new Promise(function (resolve, reject) {
//       const {username, password} = body;
//       pool.query(
//         // Taula: users_login
//         "INSERT INTO users_login (username, password) VALUES ($1, $2) RETURNING *",
//         [username, password],
//         (error, results) => {
//           if (error) {
//             reject(error);
//           }
//           if (results && results.rows) {
//             resolve(
//               `A new user has been added: ${JSON.stringify(results.rows[0])}`
//             );
//           } else {
//             reject(new Error("No results found"));
//           }
//         }
//       );
//     });
//   };

//   module.exports = {
//     createUser
//   };
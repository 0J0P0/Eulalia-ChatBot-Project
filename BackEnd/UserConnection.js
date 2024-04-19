// Connect to a PostgreSQL database using the pg library in Node.js. 
const { Pool } = require('pg');

// Create a new pool of connections.
const pool = new Pool({
  user: 'postgres',
  host: '147.83.46.71',
  password: 'password',
  database: 'usersDB',
  port: 5990,
});

// Execute a query to select all rows from table users_login. 
// Once executed, logs fetched data to the console. Then closes the connection pool.
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

// Export the connection pool
module.exports = pool;

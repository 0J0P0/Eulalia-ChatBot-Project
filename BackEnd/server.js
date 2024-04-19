// server.js
// Creates a basic Express.js server that listens on port 8081

const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');

const app = express();

app.use(express.json());
app.use(cors());

const pool = new Pool({
  user: 'postgres',
  host: '147.83.46.71',
  password: 'password',
  database: 'usersDB', // eulaliadb
  port: 5990,
});

// Send a POST request to the /login endpoint
// See if the username and password match the values provided in the request body.
app.post('/login', (req, res) => {
  const sql = "SELECT * FROM users_login WHERE username = $1 AND password = $2;";

  pool.query(sql, [req.body.username, req.body.password], (error, result) => {
    if (error) {
      return res.json("Error");
    }
    return res.json(result['rows']);
  });
});

app.listen(8081, () => {
  console.log('Server is running...');
});
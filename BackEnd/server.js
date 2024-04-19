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

app.post('/login', (req, res) => {
  const sql = "SELECT * FROM users_login WHERE username = $1 AND password = $2;";

  pool.query(sql, [req.body.username, req.body.password], (error, data) => {
    if (error) {
      return res.json("Error");
    }
    if (data.length > 0) {
      return res.json("Login successful");
    } else {
      return res.json("No record");
    }
  });
  // pool.query
  //   .then((result) => {
  //     res.send(`User added with ID: ${result.rows[0].id}`);
  //   })
  //   .catch((error) => {
  //     console.error('Error executing query', error);
  //     res.send('Error');
  //   })
});

app.listen(8081, () => {
  console.log('Server is running...');
});
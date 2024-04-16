const express = require('express')
const app = express()
const port = 3000

const users_model = require('./UserConnection')

app.use(express.json())
app.use(function (req, res, next) {
  res.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Access-Control-Allow-Headers');
  next();
});


app.post('/', (req, res) => {
  users_model.createUser(req.body)
  .then(response => {
    res.status(200).send(response);
  })
  .catch(error => {
    res.status(500).send(error);
  })
})

// app.get('/', (req, res) => {
//     res.send('Welcome to the server');
//   });

app.listen(port, () => {
  console.log(`App running on port ${port}.`)
})
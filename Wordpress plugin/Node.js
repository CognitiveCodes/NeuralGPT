const jwt = require('jsonwebtoken');

app.post('/api/authenticate', (req, res) => {
  const { username, password } = req.body;

  // Check if the username and password are correct
  if (username === 'admin' && password === 'password') {
    // Generate a JWT token
    const token = jwt.sign({ username }, 'secret-key');
    res.json({ token });
  } else {
    res.status(401).json({ message: 'Invalid credentials' });
  }
});
In your React frontend, store the JWT token in local storage:
javascript
Copy code

const [token, setToken] = useState(localStorage.getItem('token'));

const login = async (username, password) => {
  const response = await fetch('/api/authenticate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  const data = await response.json();
  if (response.ok) {
    setToken(data.token);
    localStorage.setItem('token', data.token);
  } else {
    alert(data.message);
  }
};
In your Node.js server, create a middleware function to verify the JWT token:
javascript
Copy code

const jwt = require('jsonwebtoken');

const authenticate = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (authHeader) {
    const token = authHeader.split(' ')[1];
    jwt.verify(token, 'secret-key', (err, user) => {
      if (err) {
        return res.sendStatus(403);
      }
      req.user = user;
      next();
    });
  } else {
    res.sendStatus(401);
  }
};
Use the authenticate middleware function to protect your API routes:
javascript
Copy code

app.get('/api/data', authenticate, (req, res) => {
  // Only authorized agents can access this route
  res.json({ data: 'Shared databank content' });
});
import React, { useState } from 'react';
import axios from 'axios';

function LoginForm() {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const form = new FormData();
      form.append('username', formData.username);
      form.append('password', formData.password);

      const res = await axios.post('http://localhost:9000/login', form);
      const { jwt, status } = res.data;
      if (status === 1) {
        localStorage.setItem("token", jwt);
        setMessage("Login successful! Token stored.");
      } else {
        setMessage("Login failed.");
      }
    } catch (err) {
      console.error(err);
      setMessage("Error logging in.");
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <label>Username: </label>
        <input type="text" name="username" onChange={handleChange} required />
        <label>Password: </label>
        <input type="password" name="password" onChange={handleChange} required />
        <button type="submit">Login</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default LoginForm;
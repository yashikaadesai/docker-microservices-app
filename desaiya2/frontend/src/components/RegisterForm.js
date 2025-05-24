import React, { useState } from 'react';
import axios from 'axios';

function RegisterForm() {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email_address: '',
    password: '',
    salt: '',
    employee: false,
  });

  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const form = new FormData();
      Object.entries(formData).forEach(([key, val]) => form.append(key, val));

      const res = await axios.post('http://localhost:9000/create_user', form);
      setMessage(`Registration Status: ${res.data.status}`);
    } catch (err) {
      console.error(err);
      setMessage("Something went wrong!");
    }
  };

  return (
    <div>
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        {["first_name", "last_name", "username", "email_address", "password", "salt"].map(field => (
          <div key={field}>
            <label>{field.replace("_", " ")}: </label>
            <input type={field === "password" ? "password" : "text"} name={field} onChange={handleChange} required />
          </div>
        ))}
        <label>
          Employee:
          <input type="checkbox" name="employee" onChange={handleChange} />
        </label>
        <button type="submit">Register</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default RegisterForm;
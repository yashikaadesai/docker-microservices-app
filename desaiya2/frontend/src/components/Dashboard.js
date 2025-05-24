import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Dashboard() {
  const [verified, setVerified] = useState(false);
  const [username, setUsername] = useState('');

  useEffect(() => {
    const verifyUser = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.post('http://localhost:9000/verify', {}, {
          headers: {
            "Data": token
          }
        });
        setVerified(res.data.employee);
        setUsername(res.data.username);
      } catch (err) {
        console.error(err);
      }
    };

    verifyUser();
  }, []);

  return (
    <div>
      <h2>Dashboard</h2>
      {verified ? (
        <p>Welcome, {username}! ✅ You are verified as an employee.</p>
      ) : (
        <p>Access denied or user not verified.</p>
      )}
    </div>
  );
}

export default Dashboard;
import React, { useState, useEffect } from 'react';

const BACKEND_API = 'http://localhost:5000';

const SettingsPage = () => {
  const [profile, setProfile] = useState({ full_name: '', email: '' });
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [profileMsg, setProfileMsg] = useState('');

  const [passwordForm, setPasswordForm] = useState({ current: '', new: '', confirm: '' });
  const [loadingPassword, setLoadingPassword] = useState(false);
  const [passwordMsg, setPasswordMsg] = useState('');

  useEffect(() => {
    setLoadingProfile(true);
    fetch(`${BACKEND_API}/api/users/me`)
      .then(res => res.json())
      .then(data => {
        setProfile({ full_name: data.full_name || '', email: data.email || '' });
        setLoadingProfile(false);
      })
      .catch(() => setLoadingProfile(false));
  }, []);

  const handleProfileChange = e => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleProfileSave = async e => {
    e.preventDefault();
    setLoadingProfile(true);
    setProfileMsg('');
    const res = await fetch(`${BACKEND_API}/api/users/me`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    });
    if (res.ok) {
      setProfileMsg('Profile updated successfully!');
    } else {
      setProfileMsg('Failed to update profile.');
    }
    setLoadingProfile(false);
  };

  const handlePasswordChange = e => {
    setPasswordForm({ ...passwordForm, [e.target.name]: e.target.value });
  };

  const handlePasswordUpdate = async e => {
    e.preventDefault();
    setLoadingPassword(true);
    setPasswordMsg('');
    if (passwordForm.new !== passwordForm.confirm) {
      setPasswordMsg('New passwords do not match.');
      setLoadingPassword(false);
      return;
    }
    const res = await fetch(`${BACKEND_API}/api/auth/change-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_password: passwordForm.current,
        new_password: passwordForm.new,
      }),
    });
    if (res.ok) {
      setPasswordMsg('Password updated successfully!');
      setPasswordForm({ current: '', new: '', confirm: '' });
    } else {
      setPasswordMsg('Failed to update password.');
    }
    setLoadingPassword(false);
  };

  return (
    <div className="settings-page">
      <h1 className="page-title">Settings</h1>
      <form onSubmit={handleProfileSave} className="card" style={{ marginBottom: 32, padding: 16, maxWidth: 400 }}>
        <h2>Profile</h2>
        <div className="form-group">
          <label>Full Name</label>
          <input name="full_name" type="text" value={profile.full_name} onChange={handleProfileChange} required />
        </div>
        <div className="form-group">
          <label>Email</label>
          <input name="email" type="email" value={profile.email} onChange={handleProfileChange} required />
        </div>
        <button type="submit" disabled={loadingProfile}>Save Profile</button>
        {profileMsg && <div style={{ marginTop: 8 }}>{profileMsg}</div>}
      </form>
      <form onSubmit={handlePasswordUpdate} className="card" style={{ padding: 16, maxWidth: 400 }}>
        <h2>Change Password</h2>
        <div className="form-group">
          <label>Current Password</label>
          <input name="current" type="password" value={passwordForm.current} onChange={handlePasswordChange} required />
        </div>
        <div className="form-group">
          <label>New Password</label>
          <input name="new" type="password" value={passwordForm.new} onChange={handlePasswordChange} required />
        </div>
        <div className="form-group">
          <label>Confirm New Password</label>
          <input name="confirm" type="password" value={passwordForm.confirm} onChange={handlePasswordChange} required />
        </div>
        <button type="submit" disabled={loadingPassword}>Update Password</button>
        {passwordMsg && <div style={{ marginTop: 8 }}>{passwordMsg}</div>}
      </form>
    </div>
  );
};

export default SettingsPage;
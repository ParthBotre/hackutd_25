import { useAuth0 } from "@auth0/auth0-react";
import React from "react";
import './Profile.css';

const Profile = () => {
  const { user, isAuthenticated, isLoading } = useAuth0();

  if (isLoading) {
    return <div className="profile-loading">Loading ...</div>;
  }

  return (
    isAuthenticated && (
      <div className="profile-container">
        <img src={user.picture} alt={user.name} className="profile-picture" />
        <h2 className="profile-name">{user.name}</h2>
        <p className="profile-email">{user.email}</p>
      </div>
    )
  );
};

export default Profile;


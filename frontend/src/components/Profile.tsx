/**
 * Profile component – displays the authenticated user's profile information.
 * Fetches user data from the API on mount and manages loading state.
 */
import { useEffect, useState } from "react";
import { fetchProfile } from "../services/api";

interface UserProfile {
  name: string;
  email: string;
  bio?: string;
}

const Profile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    fetchProfile()
      .then((data) => {
        if (isMounted) {
          setProfile(data);
        }
      })
      .catch((err) => {
        console.error("Failed to load profile", err);
        if (isMounted) {
          setError("Could not load profile.");
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  if (error) {
    return <div role="alert">Error: {error}</div>;
  }

  if (!profile) {
    return <div>Loading your profile...</div>;
  }

  return (
    <section className="profile-page">
      <h1>Welcome, {profile.name}!</h1>
      <p>
        <strong>Email:</strong> {profile.email}
      </p>
      {profile.bio ? <p>{profile.bio}</p> : null}
    </section>
  );
};

export default Profile;

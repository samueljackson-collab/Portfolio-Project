/** API helpers for interacting with the FastAPI backend. */
import axios from "axios";

type ProfileResponse = {
  name: string;
  email: string;
  bio?: string;
};

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
  withCredentials: true,
});

export async function fetchProfile(): Promise<ProfileResponse> {
  const response = await apiClient.get<ProfileResponse>("/users/me");
  return response.data;
}

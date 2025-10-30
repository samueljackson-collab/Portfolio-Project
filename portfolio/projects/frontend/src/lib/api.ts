import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 5000,
});

export const fetchHealth = async () => {
  const response = await api.get("/health");
  return response.data as { status: string };
};

export default api;

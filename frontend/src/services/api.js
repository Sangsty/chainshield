import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 40000,
});

export async function checkBackendHealth() {
  const response = await api.get("/");
  return response.data;
}

export async function inspectToken(tokenAddress) {
  const cleanedAddress = tokenAddress.trim();

  if (!cleanedAddress) {
    throw new Error("Token address is required.");
  }

  try {
    const response = await api.get(
      `/inspect/${encodeURIComponent(cleanedAddress)}`
    );

    return response.data;
  } catch (pathError) {
    try {
      const response = await api.get("/inspect", {
        params: {
          token_address: cleanedAddress,
        },
      });

      return response.data;
    } catch {
      throw pathError;
    }
  }
}
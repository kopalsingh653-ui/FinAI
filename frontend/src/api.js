import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const getBorrowers = async () =>
  (await api.get("/api/borrowers")).data;

export const getBorrower = async (id) =>
  (await api.get(`/api/borrowers/${id}`)).data;

export const getBorrowerApplications = async (id) =>
  (await api.get(`/api/borrowers/${id}/applications`)).data;

export const getBorrowerCreditProfile = async (id) =>
  (await api.get(`/api/borrowers/${id}/credit-profile`)).data;

export const getApplications = async () =>
  (await api.get("/api/applications")).data;

export const getApplication = async (id) =>
  (await api.get(`/api/applications/${id}`)).data;

export const getApplicationHistory = async (id) =>
  (await api.get(`/api/applications/${id}/history`)).data;

export default api;
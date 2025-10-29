// src/services/api.js
import axios from "axios";

// Instância principal do Axios
const api = axios.create({
  baseURL: "http://127.0.0.1:5000/api/v1", // URL base da API Flask
});



export default api;
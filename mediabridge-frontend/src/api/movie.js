import axios from "axios";

const API_ENDPOINT = "http://localhost:3000/api";

export const getMovie = async (id) => {
  const response = await axios.get(`${API_ENDPOINT}/movies/${id}`);
  return response.data;
};

export const getMovies = async () => {
  const response = await axios.get(`${API_ENDPOINT}/movies`);
  return response.data;
};

export const createMovie = async (movie) => {
  const response = await axios.post(`${API_ENDPOINT}/movies`, movie);
  return response.data;
};

export const updateMovie = async (id, movie) => {
  const response = await axios.put(`${API_ENDPOINT}/movies/${id}`, movie);
  return response.data;
};

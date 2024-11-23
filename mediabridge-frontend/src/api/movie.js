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

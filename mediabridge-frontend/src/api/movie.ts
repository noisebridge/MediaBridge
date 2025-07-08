import axios from "axios";

const API_ENDPOINT = "http://127.0.0.1:5000/api";

export const searchMovies = async (query: string) => {
  const response = await axios.get(`${API_ENDPOINT}/v1/movie/search`, {
    params: { q: query },
  });
  return response.data;
};

export const getRecommendations = async (movies: string[]) => {
  const response = await axios.get(`${API_ENDPOINT}/v1/movie/recommend`, {
    params: { movies },
  });
  return response.data;
};

export const getMovieById = async (id: string) => {
  const response = await axios.get(`${API_ENDPOINT}/v1/movie/${id}`);
  return response.data;
};

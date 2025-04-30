import { useState } from "react";
import { Movie } from "@/types/Movie";

export function useMovieList(initial: Movie[] = []) {
  const [movies, setMovies] = useState<Movie[]>(initial);

  const addMovie = (movie: Movie) => {
    setMovies((prev) => [...prev, movie]);
  };

  const removeMovie = (id: string) => {
    setMovies((prevMovies) => {
      return prevMovies.filter((movie) => {
        return movie.id !== id;
      });
    });
  };

  return { movies, addMovie, removeMovie };
}
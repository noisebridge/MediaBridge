import MovieList from "../components/MovieList";
import { Movie } from "../types/Movie.ts";

export const Recommendations = ({ movies }: { movies: Movie[] }) => {
  return (
    <div>
      <MovieList movies={movies} />
    </div>
  );
};

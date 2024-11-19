import MovieList from "../components/MovieList";
import MovieSearch from "../components/MovieSearch";
import { Movie } from "../types/Movie.ts";

const SelectMovies = ({ movies }: { movies: Movie[] }) => {
  return (
    <div>
      <MovieSearch />
      <button>Get Recommendations</button>
      <MovieList movies={movies} />
    </div>
  );
};

export default SelectMovies;

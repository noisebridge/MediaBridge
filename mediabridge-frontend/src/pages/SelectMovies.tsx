import MovieList from "../components/MovieList";
import MovieSearch from "../components/MovieSearch";
import { Movie } from "../types/Movie.ts";

const SelectMovies = ({
  movies,
  setMovies,
}: {
  movies: Movie[];
  setMovies: React.Dispatch<React.SetStateAction<Movie[]>>;
}) => {
  return (
    <div className="flex flex-col items-center space-y-6">
      <MovieSearch setMovies={setMovies} />
      <MovieList movies={movies} />
    </div>
  );
};

export default SelectMovies;
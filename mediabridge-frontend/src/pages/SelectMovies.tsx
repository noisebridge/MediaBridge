import MovieList from "../components/MovieList";
import MovieSearch from "../components/MovieSearch";
import { Movie } from "../types/Movie.ts";

const SelectMovies = ({
  movies,
  setMovies,
  removeMovie,
}: {
  movies: Movie[];
  setMovies: React.Dispatch<React.SetStateAction<Movie[]>>;
  removeMovie: (id: string) => void;
}) => {
  return (
    <div className="flex flex-col items-center space-y-8 w-full">
      <MovieSearch setMovies={setMovies} />
      <MovieList movies={movies} removeMovie={removeMovie} />
    </div>
  );
};

export default SelectMovies;
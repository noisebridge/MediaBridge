import MovieList from "../components/MovieList";
import MovieSearch from "../components/MovieSearch";
import { Movie } from "../types/Movie.ts";

const SelectMovies = ({
  movies,
  addMovie,
  removeMovie,
}: {
  movies: Movie[];
  addMovie: (movie: Movie) => void;
  removeMovie: (id: string) => void;
}) => {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Top full-width section */}
      <div className="w-screen">
        <div className="max-w-screen-mx flex justify-center">
          <MovieSearch movies={movies} addMovie={addMovie} />
        </div>
      </div>

      {/* Content section below */}
      <div className="px-4 py-8">
        <MovieList movies={movies} removeMovie={removeMovie} />
      </div>
    </div>
  );
};

export default SelectMovies;
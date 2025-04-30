import MovieList from "../components/MovieList";
import { Movie } from "../types/Movie.ts";

const Recommendations = ({ movies }: { movies: Movie[] }) => {
  return (
    <div>
      <MovieList movies={movies} removeMovie={() => {}} />
    </div>
  );
};

export default Recommendations;
